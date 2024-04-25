from collections import deque

import numpy as np


def add_safety(instance, prop_name, decorator):
    """Applies a decorator to the getter of a property only for a specific instance by creating a subclass."""
    subclass = type(f"{instance.__class__.__name__}Safe", (instance.__class__,), {})
    safety_attributes_key = f"_safety_attributes"

    instance.__dict__.setdefault(safety_attributes_key, [])
    instance.__dict__[safety_attributes_key].append(prop_name)

    original_property = getattr(instance.__class__, prop_name)
    if not isinstance(original_property, property):
        raise TypeError(f"The attribute {prop_name} is not a property.")

    decorated_getter = decorator(original_property.fget)
    setattr(
        subclass,
        prop_name,
        property(decorated_getter, original_property.fset, original_property.fdel),
    )
    instance.__class__ = subclass


def is_changing(attribute_name, max_points, threshold, proxy_attribute_name=None):
    """Decorator to monitor the standard deviation of an attribute's values."""
    history_key = f"_{attribute_name}_history"
    proxy_key = f"_{attribute_name}_proxy"

    def decorator(func):
        def wrapper(instance, *args, **kwargs):
            instance.__dict__.setdefault(history_key, deque(maxlen=max_points))

            try:
                if instance.__dict__[proxy_key] is True:
                    return getattr(instance, proxy_attribute_name)
            except KeyError:
                pass

            value = func(instance, *args, **kwargs)
            history = getattr(instance, history_key)
            history.append(value)
            if len(history) == max_points:  # Ensure full history before checking
                current_std = np.std(list(history))
                if current_std < threshold:
                    if proxy_attribute_name is not None:
                        print(
                            f"{attribute_name} isn't stable, returning {proxy_attribute_name}"
                        )
                        if not hasattr(instance, proxy_key):
                            setattr(instance, proxy_key, True)
                        return getattr(instance, proxy_attribute_name)
                    else:
                        raise ValueError(f"{attribute_name} is unstable")
            return value

        return wrapper

    return decorator


def is_negative(can_be_zero=True, clamp=False):
    """Decorator to check if a property's value is negative."""

    def decorator(func):
        def wrapper(instance, *args, **kwargs):
            value = func(instance, *args, **kwargs)
            if value >= 0:
                if can_be_zero and value == 0:
                    return value
                if clamp:
                    return 0
                raise ValueError("Value must be negative")
            return value

        return wrapper

    return decorator


def is_positive(can_be_zero=True, clamp=False):
    """Decorator to check if a property's value is positive."""

    def decorator(func):
        def wrapper(instance, *args, **kwargs):
            value = func(instance, *args, **kwargs)
            if value <= 0:
                if can_be_zero and value == 0:
                    return value
                if clamp:
                    return 0
                raise ValueError("Value must be positive")
            return value

        return wrapper

    return decorator


def is_within_range(min_value, max_value, clamp=False):
    """Decorator to check if a property's value is within a given range."""

    def decorator(func):
        def wrapper(instance, *args, **kwargs):
            value = func(instance, *args, **kwargs)
            if value < min_value or value > max_value:
                if clamp:
                    return min(max_value, max(min_value, value))
                raise ValueError(f"Value must be within {min_value} and {max_value}")
            return value

        return wrapper

    return decorator


if __name__ == "__main__":

    class Sensor:
        def __init__(self, value):
            self._value = value
            self._proxy_value = 0.0

        @property
        def proxy_value(self):
            return self._proxy_value

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            self._value = value

        def update(self):
            # check if there are safety attributes
            safety_attributes_key = "_safety_attributes"
            if hasattr(self, safety_attributes_key):
                print(f"Checking safety attributes for {self.__class__.__name__}")

                for attribute in getattr(self, safety_attributes_key):
                    print(f"Safety in-place for {getattr(self, attribute)}")

        def __enter__(self):
            print("Hey! I'm entering the context manager")

        def __exit__(self, exc_type, exc_val, exc_tb):
            print("Hey! I'm exiting the context manager")

    # Create two instances of the Sensor
    sensor_proxy = Sensor(100)

    with sensor_proxy:
        # Apply diagnostics only to sensor_proxy, not affecting sensor_main
        add_safety(sensor_proxy, "value", is_positive())

        # Test the result
        sensor_proxy.value = -10
        sensor_proxy.update()

        # Apply a decorator to monitor the standard deviation of the values
        add_safety(sensor_proxy, "value", is_changing("value", 5, 1e-6, "proxy_value"))
