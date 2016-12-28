import numpy as np

class Spectrometer:
    @classmethod
    def from_serial_number(cls, serial):
        print(serial + 'opened')
        return cls(serial)

    def __init__(self, serial):
        self._has_dark_pixels = True
        self._has_nonlinearity_coeffs = True
        self._serial = serial
        self._model = 'QE65000'
        self._pixels = 1044
        self._minimum_integration_time_micros = 8000
        self._temp = -15

    def integration_time_micros(self, t):
        print('set integration time to %d ms' % (t/1000))

    def spectrum(self, correct_dark_counts=False, correct_nonlinearity=False):
        return np.transpose(np.genfromtxt('test_data.csv', delimiter=','))

    def tec_set_enable(self, enable):
        print('Enable TEC: ' + str(enable))

    def tec_get_temperature_C(self):
        print('Detector temperature %.1f C' % self._temp)

    def tec_set_temperature_C(self, t):
        self._temp = t
        print('Detector temperature set to %.1f C' % self._temp)

    @property
    def serial_number(self):
        return self._serial

    @property
    def model(self):
        return self._model

    @property
    def pixels(self):
        return self._pixels

    @property
    def minimum_integration_time_micros(self):
        return self._minimum_integration_time_micros

    def close(self):
        print('Spectrometer closed')
