//
// Copyright 2015-2016 Ettus Research LLC
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

#ifndef INCLUDED_UHD_CONFIG_H
#define INCLUDED_UHD_CONFIG_H

#ifdef _MSC_VER
// Bring in "and", "or", and "not"
#include <iso646.h>

// Define ssize_t
#include <stddef.h>
typedef ptrdiff_t ssize_t;

#endif /* _MSC_VER */

// Define cross-platform macros
#if defined(_MSC_VER)
    #define UHD_EXPORT         __declspec(dllexport)
    #define UHD_IMPORT         __declspec(dllimport)
    #define UHD_INLINE         __forceinline
    #define UHD_DEPRECATED     __declspec(deprecated)
    #define UHD_ALIGNED(x)     __declspec(align(x))
    #define UHD_UNUSED(x)      x
#elif defined(__MINGW32__)
    #define UHD_EXPORT         __declspec(dllexport)
    #define UHD_IMPORT         __declspec(dllimport)
    #define UHD_INLINE         inline
    #define UHD_DEPRECATED     __declspec(deprecated)
    #define UHD_ALIGNED(x)     __declspec(align(x))
    #define UHD_UNUSED(x)      x __attribute__((unused))
#elif defined(__GNUC__) && __GNUC__ >= 4
    #define UHD_EXPORT         __attribute__((visibility("default")))
    #define UHD_IMPORT         __attribute__((visibility("default")))
    #define UHD_INLINE         inline __attribute__((always_inline))
    #define UHD_DEPRECATED     __attribute__((deprecated))
    #define UHD_ALIGNED(x)     __attribute__((aligned(x)))
    #define UHD_UNUSED(x)      x __attribute__((unused))
#elif defined(__clang__)
    #define UHD_EXPORT         __attribute__((visibility("default")))
    #define UHD_IMPORT         __attribute__((visibility("default")))
    #define UHD_INLINE         inline __attribute__((always_inline))
    #define UHD_DEPRECATED     __attribute__((deprecated))
    #define UHD_ALIGNED(x)     __attribute__((aligned(x)))
    #define UHD_UNUSED(x)      x __attribute__((unused))
#else
    #define UHD_EXPORT
    #define UHD_IMPORT
    #define UHD_INLINE         inline
    #define UHD_DEPRECATED
    #define UHD_ALIGNED(x)
    #define UHD_UNUSED(x)      x
#endif

// API declaration macro
#ifdef UHD_DLL_EXPORTS
    #define UHD_API UHD_EXPORT
#else
    #define UHD_API UHD_IMPORT
#endif // UHD_DLL_EXPORTS

// Platform defines for conditional code:
// Taken from boost/config/select_platform_config.hpp,
// However, we define macros, not strings, for platforms.
#if (defined(linux) || defined(__linux) || defined(__linux__) || defined(__GLIBC__)) && !defined(_CRAYC) && !defined(__FreeBSD_kernel__) && !defined(__GNU__)
    #define UHD_PLATFORM_LINUX
#elif defined(_WIN32) || defined(__WIN32__) || defined(WIN32)
    #define UHD_PLATFORM_WIN32
#elif defined(macintosh) || defined(__APPLE__) || defined(__APPLE_CC__)
    #define UHD_PLATFORM_MACOS
#elif defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__) || defined(__FreeBSD_kernel__)
    #define UHD_PLATFORM_BSD
#endif

#endif /* INCLUDED_UHD_CONFIG_H */
