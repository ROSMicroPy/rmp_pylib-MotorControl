# Universal Motor Control Interface

A Python-based universal interface for controlling different types of motors (Servo, Stepper, BLDC) using a driver model pattern.

## Features

- Support for multiple motor types:
  - Servo motors
  - Stepper motors
  - BLDC motors
- Driver model pattern for dynamic loading of motor behaviors
- Unified interface for all motor types
- Type safety and error checking
- Comprehensive status reporting
- Example implementations for all motor types

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/motor-control-interface.git
   cd motor-control-interface
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from motorControl import MotorController, MotorType

# Create a motor controller
controller = MotorController()

# Create a servo motor
servo = controller.create_motor(
    "servo1", 
    MotorType.SERVO, 
    "example_servo_driver",
    pin=18
)

# Control the servo
servo.set_position(90)  # Set servo to 90 degrees
print(f"Servo position: {servo.get_position()} degrees")

# Create a stepper motor
stepper = controller.create_motor(
    "stepper1", 
    MotorType.STEPPER, 
    "example_stepper_driver",
    step_pin=17,
    dir_pin=27
)

# Control the stepper
stepper.set_speed(60)  # 60 RPM
stepper.move_steps(200, True)  # Move 200 steps forward
print(f"Stepper position: {stepper.get_position()} steps")

# Create a BLDC motor
bldc = controller.create_motor(
    "bldc1", 
    MotorType.BLDC, 
    "example_bldc_driver",
    pwm_pin=22
)

# Control the BLDC
bldc.set_direction(True)  # Clockwise
bldc.set_speed(1000)  # 1000 RPM
print(f"BLDC speed: {bldc.get_speed()} RPM")

# List all motors
for motor_status in controller.list_motors():
    print(f"  {motor_status}")

# Shutdown all motors
controller.shutdown()
```

### Creating Custom Drivers

To create a custom driver for a specific motor type, you need to implement the appropriate driver class:

#### Servo Driver

```python
from motorControl import ServoDriver
from typing import Dict, Any

class MyServoDriver(ServoDriver):
    def __init__(self):
        self.position = 0.0
        self.initialized = False
    
    def initialize(self, **kwargs) -> bool:
        # Initialize your hardware here
        self.initialized = True
        return True
    
    def shutdown(self) -> bool:
        # Clean up resources
        self.initialized = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "initialized": self.initialized
        }
    
    def set_position(self, position: float) -> bool:
        # Set the servo position
        self.position = position
        return True
    
    def get_position(self) -> float:
        return self.position
```

#### Stepper Driver

```python
from motorControl import StepperDriver
from typing import Dict, Any

class MyStepperDriver(StepperDriver):
    def __init__(self):
        self.position = 0
        self.speed = 0.0
        self.initialized = False
    
    def initialize(self, **kwargs) -> bool:
        # Initialize your hardware here
        self.initialized = True
        return True
    
    def shutdown(self) -> bool:
        # Clean up resources
        self.initialized = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "speed": self.speed,
            "initialized": self.initialized
        }
    
    def move_steps(self, steps: int, direction: bool = True) -> bool:
        # Move the stepper motor
        if direction:
            self.position += steps
        else:
            self.position -= steps
        return True
    
    def set_speed(self, rpm: float) -> bool:
        # Set the stepper speed
        self.speed = rpm
        return True
    
    def get_position(self) -> int:
        return self.position
```

#### BLDC Driver

```python
from motorControl import BLDCDriver
from typing import Dict, Any

class MyBLDCDriver(BLDCDriver):
    def __init__(self):
        self.speed = 0.0
        self.clockwise = True
        self.initialized = False
    
    def initialize(self, **kwargs) -> bool:
        # Initialize your hardware here
        self.initialized = True
        return True
    
    def shutdown(self) -> bool:
        # Clean up resources
        self.initialized = False
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "speed": self.speed,
            "direction": "clockwise" if self.clockwise else "counterclockwise",
            "initialized": self.initialized
        }
    
    def set_speed(self, rpm: float) -> bool:
        # Set the BLDC speed
        self.speed = rpm
        return True
    
    def set_direction(self, clockwise: bool) -> bool:
        # Set the BLDC direction
        self.clockwise = clockwise
        return True
    
    def get_speed(self) -> float:
        return self.speed
```

## Running Examples

The repository includes example scripts that demonstrate the usage of the motor control interface:

```
python motor_examples.py
```

This will run examples for all motor types and demonstrate various features of the interface.

## Project Structure

```
motor-control-interface/
├── motorControl.py         # Main interface module
├── motor_examples.py       # Example usage scripts
├── drivers/                # Directory for motor drivers
│   ├── example_servo_driver.py
│   ├── example_stepper_driver.py
│   └── example_bldc_driver.py
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 