﻿from abc import ABC, abstractmethod
from functools import wraps

import numpy as np


class SensorNotStreamingException(Exception):
    def __init__(self, sensor_name: str = "Sensor") -> None:
        super().__init__(
            f"{sensor_name} is not streaming, please ensure that the connections are intact, power is on, and the start method is called."
        )


def check_sensor_stream(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_streaming:
            raise SensorNotStreamingException(sensor_name=self.__repr__())
        return func(self, *args, **kwargs)

    return wrapper


class SensorBase(ABC):
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"SensorBase"

    @property
    @abstractmethod
    def data(self):
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    @property
    @abstractmethod
    def is_streaming(self) -> bool:
        pass


class ADCBase(SensorBase, ABC):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return f"ADCBase"

    def reset(self) -> None:
        pass

    def calibrate(self) -> None:
        pass


class EncoderBase(SensorBase, ABC):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return f"EncoderBase"

    @property
    @abstractmethod
    def position(self) -> float:
        pass

    @property
    @abstractmethod
    def velocity(self) -> float:
        pass


class LoadcellBase(SensorBase, ABC):
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"LoadcellBase"

    @abstractmethod
    def calibrate(self) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @property
    @abstractmethod
    def fx(self) -> float:
        pass

    @property
    @abstractmethod
    def fy(self) -> float:
        pass

    @property
    @abstractmethod
    def fz(self) -> float:
        pass

    @property
    @abstractmethod
    def mx(self) -> float:
        pass

    @property
    @abstractmethod
    def my(self) -> float:
        pass

    @property
    @abstractmethod
    def mz(self) -> float:
        pass

    @property
    @abstractmethod
    def is_calibrated(self) -> bool:
        pass


class IMUBase(SensorBase, ABC):
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"IMU"

    @property
    @abstractmethod
    def acc_x(self) -> float:
        """
        Returns estimated linear acceleration along the x-axis (m/s^2).
        """
        pass

    @property
    @abstractmethod
    def acc_y(self) -> float:
        pass

    @property
    @abstractmethod
    def acc_z(self) -> float:
        pass

    @property
    @abstractmethod
    def gyro_x(self) -> float:
        pass

    @property
    @abstractmethod
    def gyro_y(self) -> float:
        pass

    @property
    @abstractmethod
    def gyro_z(self) -> float:
        pass


if __name__ == "__main__":
    pass
