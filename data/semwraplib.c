// Source: https://github.com/snapcore/snapcraft-preloads/blob/master/semaphores/preload-semaphores.c

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

/*
 * $ gcc -Wall -fPIC -shared -o mylib.so ./lib.c -ldl
 * $ LD_PRELOAD=./mylib.so ...
 */

#include <dlfcn.h>

#include <sys/types.h>
#include <stdio.h>
#include <semaphore.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdarg.h>
#include <limits.h>

static sem_t *(*original_sem_open) (const char *, int, ...);
static int (*original_sem_unlink) (const char *);

// Format is: 'sem.snap.SNAP_NAME.<something>'. So: 'sem.snap.' + '.' = 10
#define MAX_NAME_SIZE NAME_MAX - 10
#define SHM_DIR "/dev/shm"

void debug(char *s, ...)
{
	if (secure_getenv("SEMWRAP_DEBUG")) {
		va_list va;
		va_start(va, s);
		fprintf(stderr, "SEMWRAP: ");
		vfprintf(stderr, s, va);
		va_end(va);
		fprintf(stderr, "\n");
	}
}

const char *get_snap_name(void)
{
	const char *snapname = getenv("SNAP_INSTANCE_NAME");
	if (!snapname) {
		snapname = getenv("SNAP_NAME");
	}
	if (!snapname) {
		debug("SNAP_NAME and SNAP_INSTANCE_NAME not set");
	}
	return snapname;
}

int rewrite(const char *snapname, const char *name, char *rewritten,
		  size_t rmax)
{
	if (strlen(snapname) + strlen(name) > MAX_NAME_SIZE) {
		errno = ENAMETOOLONG;
		return -1;
	}

	const char *tmp = name;
	if (tmp[0] == '/') {
		// If specified with leading '/', just strip it to avoid
		// having to mkdir(), etc
		tmp = &name[1];
	}

	int n = snprintf(rewritten, rmax, "snap.%s.%s", snapname, tmp);
	if (n < 0 || n >= rmax) {
		fprintf(stderr, "snprintf truncated\n");
		return -1;
	}
	rewritten[rmax-1] = '\0';

	return 0;
}

sem_t *sem_open(const char *name, int oflag, ...)
{
	mode_t mode;
	unsigned int value;

	debug("sem_open()");
	debug("requested name: %s", name);

	// lookup the libc's sem_open() if we haven't already
	if (!original_sem_open) {
		dlerror();
		original_sem_open = dlsym(RTLD_NEXT, "sem_open");
		if (!original_sem_open) {
			debug("could not find sem_open in libc");
			return SEM_FAILED;
		}
		dlerror();
	}

	// mode and value must be set with O_CREAT
	va_list argp;
	va_start(argp, oflag);
	if (oflag & O_CREAT) {
		mode = va_arg(argp, mode_t);
		value = va_arg(argp, unsigned int);
		if (value > SEM_VALUE_MAX) {
			errno = EINVAL;
			return SEM_FAILED;
		}
	}
	va_end(argp);

	const char *snapname = get_snap_name();

	// just call libc's sem_open() if snapname not set
	if (!snapname) {
		if (oflag & O_CREAT) {
			return original_sem_open(name, oflag, mode, value);
		}
		return original_sem_open(name, oflag);
	}

	// Format the rewritten name
	char rewritten[MAX_NAME_SIZE+1];
	if (rewrite(snapname, name, rewritten, MAX_NAME_SIZE + 1) != 0) {
		return SEM_FAILED;
	}
	debug("rewritten name: %s", rewritten);

	if (oflag & O_CREAT) {
		// glibc's sem_open with O_CREAT will create a file in /dev/shm
		// by creating a tempfile, initializing it, hardlinking it and
		// unlinking the tempfile. We:
		// 1. create a temporary file in /dev/shm with rewritten path
		//    as the template and the specified mode
		// 2. initializing a sem_t with sem_init
		// 3. writing the initialized sem_t to the temporary file using
		//    sem_open()s declared value. We used '1' for pshared since
		//    that is how glibc sets up a named semaphore
		// 4. close the temporary file
		// 5. hard link the temporary file to the rewritten path. If
		//    O_EXCL is not specified, ignore EEXIST and just cleanup
		//    as per documented behavior in 'man sem_open'. If O_EXCL
		//    is specified and file exists, exit with error. If link is
		//    successful, cleanup.
		// 6. call glibc's sem_open() without O_CREAT|O_EXCL
		//
		// See glibc's fbtl/sem_open.c for more details

		// First, calculate the requested path
		char path[PATH_MAX] = { 0 };
		// /sem. + '/0' = 14
		int max_path_size = strlen(SHM_DIR) + strlen(rewritten) + 6;
		if (max_path_size >= PATH_MAX) {
			// Should never happen since PATH_MAX should be much
			// larger than NAME_MAX, but be defensive.
			errno = ENAMETOOLONG;
			return SEM_FAILED;
		}
		int n = snprintf(path, max_path_size, "%s/sem.%s", SHM_DIR,
				 rewritten);
		if (n < 0 || n >= max_path_size) {
			errno = ENAMETOOLONG;
			return SEM_FAILED;
		}
		path[max_path_size-1] = '\0';

		// Then calculate the template path
		char tmp[PATH_MAX] = { 0 };
		n = snprintf(tmp, PATH_MAX, "%s/%s.XXXXXX", SHM_DIR,
					 rewritten);
		if (n < 0 || n >= PATH_MAX) {
			errno = ENAMETOOLONG;
			return SEM_FAILED;
		}
		tmp[PATH_MAX-1] = '\0';

		// Next, create a temporary file
		int fd = mkstemp(tmp);
		if (fd < 0) {
			return SEM_FAILED;
		}
		debug("tmp name: %s", tmp);

		// Update the temporary file to have the requested mode
		if (fchmod(fd, mode) < 0) {
			close(fd);
			unlink(tmp);
			return SEM_FAILED;
		}

		// Then write out an empty semaphore and set the initial value.
		// We use '1' for pshared since that is how glibc sets up the
		// semaphore (see glibc's fbtl/sem_open.c)
		sem_t initsem;
		sem_init(&initsem, 1, value);
		if (write(fd, &initsem, sizeof(sem_t)) < 0) {
			close(fd);
			unlink(tmp);
			return SEM_FAILED;
		}
		close(fd);

		// Then link the file into place. If the target exists and
		// O_EXCL was not specified, just cleanup and proceed to open
		// the existing file as per documented behavior in 'man
		// sem_open'.
		int existed = 0;
		if (link(tmp, path) < 0) {
			// Note: snapd initially didn't allow 'l' in its
			// policy so we first try with link() since it is
			// race-free but fallback to rename() if necessary.
			if (errno == EACCES || errno == EPERM) {
				fprintf(stderr, "sem_open() wrapper: hard linking tempfile denied. Falling back to rename()\n");
				if (rename(tmp, path) < 0) {
					unlink(tmp);
					return SEM_FAILED;
				}
			} else if (oflag & O_EXCL || errno != EEXIST) {
				unlink(tmp);
				return SEM_FAILED;
			}
			existed = 1;
		}
		unlink(tmp);

		// Then call sem_open() on the created file, stripping out the
		// O_CREAT|O_EXCL since we just created it
		sem_t *sem = original_sem_open(rewritten,
									   oflag & ~(O_CREAT | O_EXCL));
		if (sem == SEM_FAILED) {
			if (!existed) {
				unlink(path);
			}
			return SEM_FAILED;
		}

		return sem;
	} else {
		// without O_CREAT, just call sem_open with rewritten
		return original_sem_open(rewritten, oflag);
	}

	return SEM_FAILED;
}

// sem_unlink
int sem_unlink(const char *name)
{
	debug("sem_unlink()");
	debug("requested name: %s", name);

	// lookup the libc's sem_unlink() if we haven't already
	if (!original_sem_unlink) {
		dlerror();
		original_sem_unlink = dlsym(RTLD_NEXT, "sem_unlink");
		if (!original_sem_unlink) {
			debug("could not find sem_unlink in libc");
			return -1;
		}
		dlerror();
	}

	const char *snapname = get_snap_name();

	// just call libc's sem_unlink() if snapname not set
	if (!snapname) {
		return original_sem_unlink(name);
	}

	// Format the rewritten name
	char rewritten[MAX_NAME_SIZE+1];
	if (rewrite(snapname, name, rewritten, MAX_NAME_SIZE + 1) != 0) {
		return -1;
	}
	debug("rewritten name: %s", rewritten);

	return original_sem_unlink(rewritten);
}