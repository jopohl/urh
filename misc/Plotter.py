import matplotlib.pyplot as plt


class Plotter(object):
    @staticmethod
    def spectrum(x, y):
        plt.plot(x, y)
        plt.title("Spectrum")
        plt.xlabel("Frequency")
        plt.ylabel("Amplitude")
        plt.show()

    @staticmethod
    def spectrum2(x1, y1, label1, x2, y2, label2):
        plt.plot(x1, y1, 'b', label=label1)
        plt.plot(x2, y2, 'r', label=label2)
        plt.title("Spectrum")
        plt.xlabel("Frequency")
        plt.ylabel("Amplitude")
        plt.legend(loc=5)
        plt.show()

    @staticmethod
    def generic_plot(*args):
        for i in range(0, len(args), 3):
            x = args[i]
            y = args[i + 1]
            l = args[i + 2]
            plt.plot(x, y, label=l)

        plt.title("Title")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend(loc=5)
        plt.show()
