#region VEXcode Generated Robot Configuration
from vex import *
import gc

brain = Brain()
print("Brain connected. Battery:", brain.battery.capacity(), "%")

PORT_MAP = {
    1: Ports.PORT1,  2: Ports.PORT2,  3: Ports.PORT3,  4: Ports.PORT4,
    5: Ports.PORT5,  6: Ports.PORT6,  7: Ports.PORT7,  8: Ports.PORT8,
    9: Ports.PORT9, 10: Ports.PORT10, 11: Ports.PORT11, 12: Ports.PORT12
}

def print_leopard():
    art = r"""
            ("`-''-/").___..--''"`-._ 
            `6_ 6  )   `-.  (     ).`-.__.`) 
            (_Y_.)'  ._   )  `._ `. ``-..-' 
            _..`--'_..-_/  /--'_.'
            ((((.-''  ((((.'  (((.-'  
    """
    print(art)


# ----------------------------------------------------------------------
# Drive motor system (left/right)
# ----------------------------------------------------------------------
class DriveMotor:
    """Dual-motor drive system for VEX IQ."""

    def __init__(self, left_port, right_port, name="Drive", default_speed_pct=50, reversed_right=True):
        self.name = name
        self.speed_pct = int(default_speed_pct)

        self.left = Motor(PORT_MAP[left_port])
        self.right = Motor(PORT_MAP[right_port])

        for m in (self.left, self.right):
            try: m.set_stopping(BRAKE)
            except Exception: pass
            try: m.set_velocity(self.speed_pct, PERCENT)
            except Exception: pass
            try: m.set_position(0, DEGREES)
            except Exception: pass

        try: self.right.set_reversed(bool(reversed_right))
        except Exception: pass

        print("%s ready: left=%d right=%d" % (self.name, left_port, right_port))

    def _stop(self):
        try: self.left.stop()
        except Exception: pass
        try: self.right.stop()
        except Exception: pass

    def forward(self, rotations=1.0, speed_pct=None):
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception: pass
        print("Driving forward %.2f rotations..." % rotations)
        try:
            self.left.spin_for(FORWARD, rotations, TURNS, False)
            self.right.spin_for(FORWARD, rotations, TURNS, True)
        except Exception:
            self.left.spin(FORWARD)
            self.right.spin(FORWARD)
            wait(1000, MSEC)
        self._stop()

    def backward(self, rotations=1.0, speed_pct=None):
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception: pass
        print("Driving backward %.2f rotations..." % rotations)
        try:
            self.left.spin_for(REVERSE, rotations, TURNS, False)
            self.right.spin_for(REVERSE, rotations, TURNS, True)
        except Exception:
            self.left.spin(REVERSE)
            self.right.spin(REVERSE)
            wait(1000, MSEC)
        self._stop()

    def turn_left(self, degrees=90, speed_pct=None):
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception: pass
        print("Turning left %d°..." % degrees)
        turn_rot = degrees / 90.0 * 0.5
        try:
            self.left.spin_for(REVERSE, turn_rot, TURNS, False)
            self.right.spin_for(FORWARD, turn_rot, TURNS, True)
        except Exception:
            self.left.spin(REVERSE)
            self.right.spin(FORWARD)
            wait(800, MSEC)
        self._stop()

    def turn_right(self, degrees=90, speed_pct=None):
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception: pass
        print("Turning right %d°..." % degrees)
        turn_rot = degrees / 90.0 * 0.5
        try:
            self.left.spin_for(FORWARD, turn_rot, TURNS, False)
            self.right.spin_for(REVERSE, turn_rot, TURNS, True)
        except Exception:
            self.left.spin(FORWARD)
            self.right.spin(REVERSE)
            wait(800, MSEC)
        self._stop()


# ----------------------------------------------------------------------
# Claw motor
# ----------------------------------------------------------------------
class ClawMotor:
    """Claw motor that closes until stall and opens for a short duration."""

    def __init__(self, port_number, name="Claw", speed_pct=40, reversed=False, backoff_deg=6):
        self.name = name
        self.m = Motor(PORT_MAP[port_number])
        self.speed_pct = int(speed_pct)
        self.backoff_deg = int(backoff_deg)

        try: self.m.set_stopping(HOLD)
        except Exception: pass
        try: self.m.set_velocity(self.speed_pct, PERCENT)
        except Exception: pass
        try: self.m.set_reversed(bool(reversed))
        except Exception: pass
        try: self.m.set_position(0, DEGREES)
        except Exception: pass

    def _stop(self):
        try: self.m.stop()
        except Exception: pass

    def _pos(self):
        try: return self.m.position(DEGREES)
        except Exception: return None

    def _vel(self):
        try: return self.m.velocity()
        except Exception: return None

    def close(self, timeout_ms=3000):
        print("Closing claw...")
        try: self.m.spin(REVERSE)
        except Exception: return

        step = 20; elapsed = 0; still_elapsed = 0; last_pos = self._pos()
        while elapsed < timeout_ms:
            pos = self._pos(); vel = self._vel()
            moved = pos is not None and last_pos is not None and abs(pos - last_pos) > 0.15
            if moved: still_elapsed = 0
            else:
                if vel is None or abs(vel) < 1: still_elapsed += step
            if still_elapsed >= 350: break
            last_pos = pos; wait(step, MSEC); elapsed += step

        self._stop()
        if self.backoff_deg > 0:
            try: self.m.spin_for(self.backoff_deg, DEGREES, True)
            except Exception:
                self.m.spin(FORWARD); wait(120, MSEC); self._stop()
        print("Claw closed. pos=%s°" % str(self._pos()))

    def open(self, ms=600, speed_pct=None):
        if speed_pct is not None:
            try: self.m.set_velocity(int(speed_pct), PERCENT)
            except Exception: pass
        print("Opening claw...")
        try:
            self.m.spin(FORWARD); wait(int(ms), MSEC)
        finally:
            self._stop()
        print("Claw opened. pos=%s°" % str(self._pos()))


class LiftMotor:
    """Simple lift motor that moves up/down by a fixed number of rotations."""
    
    def __init__(self, port_num=10, default_speed_pct=50, reversed=False):
        port = getattr(Ports, 'PORT%d' % int(port_num))
        self.m = Motor(port)
        self.spd = int(default_speed_pct)

        try: self.m.set_stopping(HOLD)
        except: pass
        try: self.m.set_velocity(self.spd, PERCENT)
        except: pass
        try: self.m.set_reversed(bool(reversed))
        except: pass
        try: self.m.set_position(0, DEGREES)
        except: pass

        print("Lift ready on port %d, speed=%d%%" % (port_num, self.spd))

    def up_by(self, rotations=0.5, speed_pct=None):
        """Move lift up by X motor rotations."""
        gc.collect()
        if speed_pct is not None:
            try: self.m.set_velocity(int(speed_pct), PERCENT)
            except: pass
        else:
            try: self.m.set_velocity(self.spd, PERCENT)
            except: pass

        print("Lift: up %.2f rotations" % rotations)
        try:
            self.m.spin_for(FORWARD, rotations, TURNS, True)
        except:
            self.m.spin(FORWARD)
            wait(int(1000 * rotations), MSEC)
            self.m.stop()
        gc.collect()

    def down_by(self, rotations=0.5, speed_pct=None):
        """Move lift down by X motor rotations."""
        gc.collect()
        if speed_pct is not None:
            try: self.m.set_velocity(int(speed_pct), PERCENT)
            except: pass
        else:
            try: self.m.set_velocity(self.spd, PERCENT)
            except: pass

        print("Lift: down %.2f rotations" % rotations)
        try:
            self.m.spin_for(REVERSE, rotations, TURNS, True)
        except:
            self.m.spin(REVERSE)
            wait(int(1000 * rotations), MSEC)
            self.m.stop()
        gc.collect()

    def stop(self):
        """Stop lift immediately."""
        try: self.m.stop()
        except: pass



# ----------------------------------------------------------------------
# Test helpers
# ----------------------------------------------------------------------
def test_claw(claw):
    print("\nOpening claw..."); claw.open()
    print("Closing claw..."); claw.close()

def test_drive(drive):
    drive.forward(rotations=2); wait(300, MSEC)
    drive.backward(rotations=1); wait(300, MSEC)
    drive.turn_left(degrees=90); wait(300, MSEC)
    drive.turn_right(degrees=90); wait(300, MSEC)

def test_lift(lift):
    lift.down_by(2); 
    wait(500, MSEC)
    lift.up_by(2);
    wait(500, MSEC)
    print("Lift test complete.")


# ----------------------------------------------------------------------
# Main sequence
# ----------------------------------------------------------------------
def main():
    print_leopard()
    print("Leopards ready?")
    print("Brain connected. Battery: %d %%" % brain.battery.capacity())

    claw = ClawMotor(port_number=9, name="Claw", speed_pct=60, reversed=False)
    drive = DriveMotor(left_port=12, right_port=11, default_speed_pct=50)
    lift = LiftMotor(port_num=10, default_speed_pct=80, reversed=False)
    test_lift(lift)

    # # example demo
    # claw.open(); 
    # claw.close()
    # #lift.up_by(0.9)
    
    # drive.turn_left(degrees=45)
    # drive.forward(rotations=3)
    
    # #lift.down_by(.9)
    # claw.open()
    
    # drive.backward(rotations=1)

main()
