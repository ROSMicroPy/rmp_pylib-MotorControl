#!/usr/bin/env python3
"""
Universal Motor Control Interface

This module provides a universal interface for controlling different types of motors
(Servo, Stepper, BLDC) using a driver model pattern. The interface allows for dynamic
loading of motor drivers based on the motor type.

Example:
    >>> from motorControl import MotorController, MotorType
    >>> controller = MotorController()
    >>> servo = controller.create_motor("servo1", MotorType.SERVO, driver_name="pca9685")
    >>> servo.set_position(90)  # Set servo to 90 degrees
    >>> stepper = controller.create_motor("stepper1", MotorType.STEPPER, driver_name="a4988")
    >>> stepper.move_steps(200)  # Move stepper 200 steps
"""

import importlib
import inspect
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, Type, List


class MotorType(Enum):
    """Enumeration of supported motor types."""
    SERVO = "servo"
    STEPPER = "stepper"
    BLDC = "bldc"


class MotorDriver(ABC):
    """Abstract base class for motor drivers."""
    
    @abstractmethod
    def initialize(self, **kwargs) -> bool:
        """Initialize the motor driver with the given parameters."""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the motor driver and release resources."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the motor."""
        pass


class ServoDriver(MotorDriver):
    """Base class for servo motor drivers."""
    
    @abstractmethod
    def set_position(self, position: float) -> bool:
        """Set the servo position in degrees (0-180)."""
        pass
    
    @abstractmethod
    def get_position(self) -> float:
        """Get the current servo position in degrees."""
        pass


class StepperDriver(MotorDriver):
    """Base class for stepper motor drivers."""
    
    @abstractmethod
    def move_steps(self, steps: int, direction: bool = True) -> bool:
        """Move the stepper motor by the specified number of steps."""
        pass
    
    @abstractmethod
    def set_speed(self, rpm: float) -> bool:
        """Set the stepper motor speed in RPM."""
        pass
    
    @abstractmethod
    def get_position(self) -> int:
        """Get the current position in steps."""
        pass


class BLDCDriver(MotorDriver):
    """Base class for BLDC motor drivers."""
    
    @abstractmethod
    def set_speed(self, rpm: float) -> bool:
        """Set the BLDC motor speed in RPM."""
        pass
    
    @abstractmethod
    def set_direction(self, clockwise: bool) -> bool:
        """Set the BLDC motor direction."""
        pass
    
    @abstractmethod
    def get_speed(self) -> float:
        """Get the current BLDC motor speed in RPM."""
        pass


class Motor:
    """Universal motor interface that wraps a specific motor driver."""
    
    def __init__(self, name: str, motor_type: MotorType, driver: MotorDriver):
        self.name = name
        self.motor_type = motor_type
        self.driver = driver
        self.initialized = False
    
    def initialize(self, **kwargs) -> bool:
        """Initialize the motor driver."""
        if not self.initialized:
            self.initialized = self.driver.initialize(**kwargs)
        return self.initialized
    
    def shutdown(self) -> bool:
        """Shutdown the motor driver."""
        if self.initialized:
            self.initialized = not self.driver.shutdown()
        return not self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the motor."""
        status = self.driver.get_status()
        status.update({
            "name": self.name,
            "type": self.motor_type.value,
            "initialized": self.initialized
        })
        return status
    
    # Servo-specific methods
    def set_position(self, position: float) -> bool:
        """Set the servo position in degrees (0-180)."""
        if not isinstance(self.driver, ServoDriver):
            raise TypeError(f"Motor {self.name} is not a servo motor")
        return self.driver.set_position(position)
    
    def get_position(self) -> float:
        """Get the current servo position in degrees."""
        if not isinstance(self.driver, ServoDriver):
            raise TypeError(f"Motor {self.name} is not a servo motor")
        return self.driver.get_position()
    
    # Stepper-specific methods
    def move_steps(self, steps: int, direction: bool = True) -> bool:
        """Move the stepper motor by the specified number of steps."""
        if not isinstance(self.driver, StepperDriver):
            raise TypeError(f"Motor {self.name} is not a stepper motor")
        return self.driver.move_steps(steps, direction)
    
    def set_speed(self, rpm: float) -> bool:
        """Set the motor speed in RPM."""
        if isinstance(self.driver, StepperDriver):
            return self.driver.set_speed(rpm)
        elif isinstance(self.driver, BLDCDriver):
            return self.driver.set_speed(rpm)
        else:
            raise TypeError(f"Motor {self.name} does not support speed control")
    
    def get_stepper_position(self) -> int:
        """Get the current stepper position in steps."""
        if not isinstance(self.driver, StepperDriver):
            raise TypeError(f"Motor {self.name} is not a stepper motor")
        return self.driver.get_position()
    
    # BLDC-specific methods
    def set_direction(self, clockwise: bool) -> bool:
        """Set the BLDC motor direction."""
        if not isinstance(self.driver, BLDCDriver):
            raise TypeError(f"Motor {self.name} is not a BLDC motor")
        return self.driver.set_direction(clockwise)
    
    def get_speed(self) -> float:
        """Get the current motor speed in RPM."""
        if isinstance(self.driver, StepperDriver):
            return self.driver.speed
        elif isinstance(self.driver, BLDCDriver):
            return self.driver.get_speed()
        else:
            raise TypeError(f"Motor {self.name} does not support speed control")


class MotorController:
    """Controller for managing multiple motors with different drivers."""
    
    def __init__(self, driver_path: str = "drivers"):
        """
        Initialize the motor controller.
        
        Args:
            driver_path: Path to the directory containing motor driver modules.
        """
        self.motors: Dict[str, Motor] = {}
        self.driver_path = driver_path
        self.driver_cache: Dict[str, Type[MotorDriver]] = {}
    
    def _load_driver(self, driver_name: str) -> Type[MotorDriver]:
        """Load a motor driver module by name."""
        if driver_name in self.driver_cache:
            return self.driver_cache[driver_name]
        
        try:
            # Try to import the driver module
            module = importlib.import_module(f"{self.driver_path}.{driver_name}")
            
            # Find the driver class in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, MotorDriver) and 
                    obj != MotorDriver and 
                    obj != ServoDriver and 
                    obj != StepperDriver and 
                    obj != BLDCDriver):
                    self.driver_cache[driver_name] = obj
                    return obj
            
            raise ImportError(f"No valid driver class found in {driver_name}")
        except ImportError as e:
            raise ImportError(f"Failed to load driver {driver_name}: {e}")
    
    def create_motor(self, name: str, motor_type: MotorType, 
                    driver_name: str, **kwargs) -> Motor:
        """
        Create a new motor with the specified driver.
        
        Args:
            name: Unique name for the motor.
            motor_type: Type of motor (SERVO, STEPPER, BLDC).
            driver_name: Name of the driver module to use.
            **kwargs: Additional parameters for the motor driver.
            
        Returns:
            A new Motor instance.
            
        Raises:
            ValueError: If a motor with the given name already exists.
            ImportError: If the specified driver cannot be loaded.
            TypeError: If the driver is not compatible with the motor type.
        """
        if name in self.motors:
            raise ValueError(f"Motor with name {name} already exists")
        
        driver_class = self._load_driver(driver_name)
        driver = driver_class()
        
        # Verify driver compatibility with motor type
        if motor_type == MotorType.SERVO and not isinstance(driver, ServoDriver):
            raise TypeError(f"Driver {driver_name} is not compatible with servo motors")
        elif motor_type == MotorType.STEPPER and not isinstance(driver, StepperDriver):
            raise TypeError(f"Driver {driver_name} is not compatible with stepper motors")
        elif motor_type == MotorType.BLDC and not isinstance(driver, BLDCDriver):
            raise TypeError(f"Driver {driver_name} is not compatible with BLDC motors")
        
        motor = Motor(name, motor_type, driver)
        motor.initialize(**kwargs)
        self.motors[name] = motor
        return motor
    
    def get_motor(self, name: str) -> Optional[Motor]:
        """Get a motor by name."""
        return self.motors.get(name)
    
    def remove_motor(self, name: str) -> bool:
        """Remove a motor by name."""
        if name in self.motors:
            motor = self.motors[name]
            motor.shutdown()
            del self.motors[name]
            return True
        return False
    
    def list_motors(self) -> List[Dict[str, Any]]:
        """List all motors and their status."""
        return [motor.get_status() for motor in self.motors.values()]
    
    def shutdown(self):
        """Shutdown all motors."""
        for motor in self.motors.values():
            motor.shutdown()
        self.motors.clear()
        self.driver_cache.clear()


# Example driver implementations
class ExampleServoDriver(ServoDriver):
    """Example implementation of a servo driver."""
    
    def __init__(self):
        self.position = 0.0
        self.initialized = False
    
    def initialize(self, **kwargs) -> bool:
        print(f"Initializing servo driver with params: {kwargs}")
        self.initialized = True
        return True
    
    def shutdown(self) -> bool:
        print("Shutting down servo driver")
        self.initialized = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "initialized": self.initialized
        }
    
    def set_position(self, position: float) -> bool:
        if not self.initialized:
            return False
        self.position = max(0.0, min(180.0, position))
        print(f"Setting servo position to {self.position} degrees")
        return True
    
    def get_position(self) -> float:
        return self.position


class ExampleStepperDriver(StepperDriver):
    """Example implementation of a stepper driver."""
    
    def __init__(self):
        self.position = 0
        self.speed = 0.0
        self.initialized = False
    
    def initialize(self, **kwargs) -> bool:
        print(f"Initializing stepper driver with params: {kwargs}")
        self.initialized = True
        return True
    
    def shutdown(self) -> bool:
        print("Shutting down stepper driver")
        self.initialized = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "speed": self.speed,
            "initialized": self.initialized
        }
    
    def move_steps(self, steps: int, direction: bool = True) -> bool:
        if not self.initialized:
            return False
        if direction:
            self.position += steps
        else:
            self.position -= steps
        print(f"Moving stepper {steps} steps {'forward' if direction else 'backward'}")
        return True
    
    def set_speed(self, rpm: float) -> bool:
        if not self.initialized:
            return False
        self.speed = max(0.0, rpm)
        print(f"Setting stepper speed to {self.speed} RPM")
        return True
    
    def get_position(self) -> int:
        return self.position


class ExampleBLDCDriver(BLDCDriver):
    """Example implementation of a BLDC driver."""
    
    def __init__(self):
        self.speed = 0.0
        self.clockwise = True
        self.initialized = False
    
    def initialize(self, **kwargs) -> bool:
        print(f"Initializing BLDC driver with params: {kwargs}")
        self.initialized = True
        return True
    
    def shutdown(self) -> bool:
        print("Shutting down BLDC driver")
        self.initialized = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "speed": self.speed,
            "direction": "clockwise" if self.clockwise else "counterclockwise",
            "initialized": self.initialized
        }
    
    def set_speed(self, rpm: float) -> bool:
        if not self.initialized:
            return False
        self.speed = max(0.0, rpm)
        print(f"Setting BLDC speed to {self.speed} RPM")
        return True
    
    def set_direction(self, clockwise: bool) -> bool:
        if not self.initialized:
            return False
        self.clockwise = clockwise
        print(f"Setting BLDC direction to {'clockwise' if clockwise else 'counterclockwise'}")
        return True
    
    def get_speed(self) -> float:
        return self.speed


# Example usage
if __name__ == "__main__":
    # Create a motor controller
    controller = MotorController()
    
    try:
        # Create a servo motor
        servo = controller.create_motor(
            "servo1", 
            MotorType.SERVO, 
            "example_servo_driver",
            pin=18
        )
        
        # Create a stepper motor
        stepper = controller.create_motor(
            "stepper1", 
            MotorType.STEPPER, 
            "example_stepper_driver",
            step_pin=17,
            dir_pin=27
        )
        
        # Create a BLDC motor
        bldc = controller.create_motor(
            "bldc1", 
            MotorType.BLDC, 
            "example_bldc_driver",
            pwm_pin=22
        )
        
        # Control the servo
        servo.set_position(90)
        print(f"Servo position: {servo.get_position()} degrees")
        
        # Control the stepper
        stepper.set_speed(60)  # 60 RPM
        stepper.move_steps(200, True)  # Move 200 steps forward
        print(f"Stepper position: {stepper.get_stepper_position()} steps")
        
        # Control the BLDC
        bldc.set_direction(True)  # Clockwise
        bldc.set_speed(1000)  # 1000 RPM
        print(f"BLDC speed: {bldc.get_speed()} RPM")
        
        # List all motors
        print("\nAll motors:")
        for motor_status in controller.list_motors():
            print(f"  {motor_status}")
        
    finally:
        # Shutdown all motors
        controller.shutdown()
