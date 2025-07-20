#!/usr/bin/env python3
"""
Motor Control Interface Examples

This script demonstrates the usage of the universal motor control interface
with different types of motors (Servo, Stepper, BLDC) and drivers.
"""

import time
from motorControl import MotorController, MotorType


def servo_example(controller: MotorController):
    """Example of controlling a servo motor."""
    print("\n=== Servo Motor Example ===")
    
    # Create a servo motor
    servo = controller.create_motor(
        "servo1",
        MotorType.SERVO,
        "example_servo_driver",
        pin=18
    )
    
    # Move to different positions
    positions = [0, 45, 90, 135, 180]
    for pos in positions:
        print(f"\nMoving servo to {pos} degrees")
        servo.set_position(pos)
        print(f"Current position: {servo.get_position()} degrees")
    
    # Get motor status
    print("\nServo status:")
    status = servo.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")


def stepper_example(controller: MotorController):
    """Example of controlling a stepper motor."""
    print("\n=== Stepper Motor Example ===")
    
    # Create a stepper motor
    stepper = controller.create_motor(
        "stepper1",
        MotorType.STEPPER,
        "example_stepper_driver",
        step_pin=17,
        dir_pin=27,
        enable_pin=22,
        microsteps=16
    )
    
    # Set speed and move
    print("\nSetting speed to 60 RPM")
    stepper.set_speed(60)
    
    # Move forward
    print("\nMoving 200 steps forward")
    stepper.move_steps(200, True)
    print(f"Current position: {stepper.get_stepper_position()} steps")
    
    # Move backward
    print("\nMoving 100 steps backward")
    stepper.move_steps(100, False)
    print(f"Current position: {stepper.get_stepper_position()} steps")
    
    # Get motor status
    print("\nStepper status:")
    status = stepper.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")


def bldc_example(controller: MotorController):
    """Example of controlling a BLDC motor."""
    print("\n=== BLDC Motor Example ===")
    
    # Create a BLDC motor
    bldc = controller.create_motor(
        "bldc1",
        MotorType.BLDC,
        "example_bldc_driver",
        pwm_pin=22,
        hall_sensor_pins=[23, 24, 25],
        max_speed=5000
    )
    
    # Set direction and speed
    print("\nSetting direction to clockwise")
    bldc.set_direction(True)
    
    # Ramp up speed
    print("\nRamping up speed")
    for speed in range(0, 5001, 1000):
        bldc.set_speed(speed)
        print(f"Current speed: {bldc.get_speed()} RPM")
    
    # Change direction
    print("\nChanging direction to counterclockwise")
    bldc.set_direction(False)
    
    # Ramp down speed
    print("\nRamping down speed")
    for speed in range(5000, -1, -1000):
        bldc.set_speed(speed)
        print(f"Current speed: {bldc.get_speed()} RPM")
    
    # Get motor status
    print("\nBLDC status:")
    status = bldc.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")


def multi_motor_example(controller: MotorController):
    """Example of controlling multiple motors simultaneously."""
    print("\n=== Multi-Motor Example ===")
    
    # Create all motor types
    servo = controller.create_motor(
        "servo2",
        MotorType.SERVO,
        "example_servo_driver",
        pin=18
    )
    
    stepper = controller.create_motor(
        "stepper2",
        MotorType.STEPPER,
        "example_stepper_driver",
        step_pin=17,
        dir_pin=27,
        enable_pin=22
    )
    
    bldc = controller.create_motor(
        "bldc2",
        MotorType.BLDC,
        "example_bldc_driver",
        pwm_pin=22
    )
    
    # Set initial states
    print("\nSetting initial states:")
    servo.set_position(90)
    stepper.set_speed(30)
    bldc.set_direction(True)
    bldc.set_speed(1000)
    
    # Move all motors
    print("\nMoving all motors:")
    servo.set_position(45)
    stepper.move_steps(100, True)
    bldc.set_speed(2000)
    
    # Get status of all motors
    print("\nAll motors status:")
    for motor_status in controller.list_motors():
        print(f"\nMotor: {motor_status['name']}")
        for key, value in motor_status.items():
            if key != 'name':
                print(f"  {key}: {value}")


def run_all_examples():
    """Run all motor control examples."""
    controller = MotorController()
    
    try:
        # Run individual examples
        servo_example(controller)
        stepper_example(controller)
        bldc_example(controller)
        multi_motor_example(controller)
        
        print("\nAll examples completed successfully!")
        
    finally:
        # Clean up
        controller.shutdown()


if __name__ == "__main__":
    run_all_examples() 