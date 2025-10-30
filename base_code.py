#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

# Brain should be defined by default
brain=Brain()

# Robot configuration code
brain_inertial = Inertial()
# AI Classification Classroom Element IDs
class ClassroomElements:
    BLUE_BALL = 0
    GREEN_BALL = 1
    RED_BALL = 2
    BLUE_RING = 3
    GREEN_RING = 4
    RED_RING = 5
    BLUE_CUBE = 6
    GREEN_CUBE = 7
    RED_CUBE = 8
# AI Vision Color Descriptions
# AI Vision Code Descriptions
ai_vision_sensor = AiVision(Ports.PORT2, AiVision.ALL_AIOBJS)



# generating and setting random seed
def initializeRandomSeed():
    wait(100, MSEC)
    xaxis = brain_inertial.acceleration(XAXIS) * 1000
    yaxis = brain_inertial.acceleration(YAXIS) * 1000
    zaxis = brain_inertial.acceleration(ZAXIS) * 1000
    systemTime = brain.timer.system() * 100
    urandom.seed(int(xaxis + yaxis + zaxis + systemTime)) 
    
# Initialize random seed 
initializeRandomSeed()

#endregion VEXcode Generated Robot Configuration
from vex import *


brain = Brain()
print("Brain connected. Battery:", brain.battery.capacity(), "%")

# Map port number -> Ports.PORT#
PORT_MAP = {
    1: Ports.PORT1,  2: Ports.PORT2,  3: Ports.PORT3,  4: Ports.PORT4,
    5: Ports.PORT5,  6: Ports.PORT6,  7: Ports.PORT7,  8: Ports.PORT8,
    9: Ports.PORT9, 10: Ports.PORT10, 11: Ports.PORT11, 12: Ports.PORT12
}

# Check that the AI Vision Sensor device variable exists
try:
    vs = ai_vision_sensor          # matches your Devices name
    print("✅ Found AI Vision Sensor (vision_1) on Port 2.")
except NameError:
    print("❌ Vision Sensor not found.  Add it in Devices → AI Vision Sensor → Port 2.")
    raise SystemExit()


# --- Helper function ---
def detect_mixmatch_objects(sensor):
    """Detects AI-classified objects from the Mix & Match model."""
    objs = sensor.take_snapshot(AiVision.ALL_AIOBJS)
    if not objs or len(sensor.objects) == 0:
        print("No Mix & Match objects detected.")
        return []

    results = []
    for o in sensor.objects:
        label = "ID:" + str(o.id)
        # Optional label lookup for better readability
        try:
            label_map = {
                GameElementsMixAndMatch.ORANGE_PIN: "ORANGE_PIN",
                GameElementsMixAndMatch.RED_PIN: "RED_PIN",
                GameElementsMixAndMatch.BLUE_PIN: "BLUE_PIN",
                GameElementsMixAndMatch.BEAM: "BEAM",
            }
            label = label_map.get(o.id, label)
        except NameError:
            pass

        # Print details to console
        print(label, "| Center:", (o.centerX, o.centerY),
              "| Size:", (o.width, o.height),
              "| Score:", getattr(o, "score", "n/a"))

        results.append({
            "id": o.id,
            "label": label,
            "center": (o.centerX, o.centerY),
            "size": (o.width, o.height),
            "score": getattr(o, "score", None)
        })

    return results

def detect_classroom_objects(sensor):
    # 1) Ensure API symbol exists
    if not hasattr(AiVision, "ALL_AIOBJS"):
        print("AI Classification API not available. Update VEXos/VEXcode.")
        return []

    # 2) Snapshot
    ok = sensor.take_snapshot(AiVision.ALL_AIOBJS)

    # 3) Defensive checks + explicit reasons
    if not ok:
        print("AI snapshot returned False (model not active or not saved).")
        return []

    if not hasattr(sensor, "objects"):
        print("Sensor has no 'objects' attribute yet (firmware behavior).")
        return []

    if len(sensor.objects) == 0:
        print("AI model active but saw 0 objects. Check distance/lighting/FOV.")
        return []

    # 4) Label map (if enums present)
    try:
        label_map = {
            GameElementsClassroomObjects.BALL:     "BALL",
            GameElementsClassroomObjects.CUBE:     "CUBE",
            GameElementsClassroomObjects.CONE:     "CONE",
            GameElementsClassroomObjects.CYLINDER: "CYLINDER",
            GameElementsClassroomObjects.PERSON:   "PERSON",
        }
    except NameError:
        label_map = {}

    results = []
    for o in sensor.objects:
        obj_id = getattr(o, "id", "?")
        label = label_map.get(obj_id, "ID:" + str(obj_id))
        print(label,
              "| center:", (o.centerX, o.centerY),
              "| size:", (o.width, o.height),
              "| score:", getattr(o, "score", "n/a"))
        results.append({
            "label": label,
            "center": (o.centerX, o.centerY),
            "size": (o.width, o.height),
            "score": getattr(o, "score", None)
        })
    return results


def print_leopard():
    art = r"""
("`-''-/").___..--''"`-._ 
 `6_ 6  )   `-.  (     ).`-.__.`) 
 (_Y_.)'  ._   )  `._ `. ``-..-' 
   _..`--'_..-_/  /--'_.'
  ((((.-''  ((((.'  (((.-'  
    """
    print(art)


def _nearly_equal(a, b, tol):
    return abs(a - b) <= tol

class MotorBase(object):
    def __init__(self, port_number, name="Motor", default_speed_pct=50, reversed=False):
        if port_number not in PORT_MAP:
            raise ValueError("Invalid port number: %d" % port_number)
        self.port_number = port_number
        self.name = name
        self.m = Motor(PORT_MAP[port_number])

        try: self.m.set_stopping(HOLD)
        except Exception: pass
        try: self.m.set_velocity(int(default_speed_pct), PERCENT)
        except Exception: pass
        try: self.m.set_reversed(bool(reversed))
        except Exception: pass
        try: self.m.set_position(0, DEGREES)
        except Exception: pass

    def position_deg(self):
        try: return self.m.position(DEGREES)
        except Exception: return None

    def velocity_pct(self):
        try: return self.m.velocity()
        except Exception: return None

    def _set_speed(self, pct):
        try: self.m.set_velocity(int(pct), PERCENT)
        except Exception: pass

    def _stop(self):
        try: self.m.stop()
        except Exception: pass

    def _move_with_watchdog(self, start_callable, target_deg, timeout_ms=2500,
                            settle_tol_deg=2, no_progress_ms=400):
        """
        start_callable(): starts a NON-BLOCKING move (spin_to_position(..., wait=False) or spin_for(..., wait=False))
        We then poll until target reached, timeout, or no-progress stall.
        """
        # start move
        try:
            start_callable()
        except Exception:
            return False

        start_pos = self.position_deg()
        last_pos = start_pos
        elapsed = 0
        no_prog_elapsed = 0
        step = 20

        while elapsed < timeout_ms:
            pos = self.position_deg()
            vel = self.velocity_pct()

            # Success if close to target
            if pos is not None and _nearly_equal(pos, target_deg, settle_tol_deg):
                self._stop()
                return True

            # Progress check
            if pos is not None and last_pos is not None:
                if abs(pos - last_pos) < 0.2:  # ~no movement this tick
                    no_prog_elapsed += step
                else:
                    no_prog_elapsed = 0
            else:
                # can't read position -> rely on time/vel
                if vel is not None and abs(vel) < 1:
                    no_prog_elapsed += step

            # Stall or blocked
            if no_prog_elapsed >= no_progress_ms:
                self._stop()
                return False

            last_pos = pos
            wait(step, MSEC)
            elapsed += step

        # Timeout
        self._stop()
        return False

    def _move_abs_safe(self, target_deg, speed_pct=None, timeout_ms=2500):
        if speed_pct is not None:
            self._set_speed(speed_pct)

        # Try absolute non-blocking if available
        def _start_abs():
            # Some builds: wait=False form
            self.m.spin_to_position(int(target_deg), DEGREES, False)

        try:
            return self._move_with_watchdog(_start_abs, int(target_deg), timeout_ms)
        except Exception:
            pass

        # Fallback to relative non-blocking
        pos = self.position_deg()
        if pos is None:
            return False
        delta = int(target_deg - pos)

        def _start_rel():
            self.m.spin_for(delta, DEGREES, False)

        return self._move_with_watchdog(_start_rel, int(target_deg), timeout_ms)

class DriveMotor:
    """
    Dual-motor drive system for VEX IQ.
    Controls left and right motors for forward, backward, and turns.
    """

    def __init__(self, left_port, right_port, name="Drive", default_speed_pct=50, reversed_right=True):
        self.name = name
        self.speed_pct = int(default_speed_pct)

        # Initialize motors
        self.left = Motor(PORT_MAP[left_port])
        self.right = Motor(PORT_MAP[right_port])

        # Configure both
        for m in (self.left, self.right):
            try: m.set_stopping(BRAKE)
            except Exception: pass
            try: m.set_velocity(self.speed_pct, PERCENT)
            except Exception: pass
            try: m.set_position(0, DEGREES)
            except Exception: pass

        # Optional: reverse one side so both go forward properly
        try: self.right.set_reversed(bool(reversed_right))
        except Exception: pass

        print("%s ready: left=%d right=%d" % (self.name, left_port, right_port))

    def _stop(self):
        try: self.left.stop()
        except Exception: pass
        try: self.right.stop()
        except Exception: pass

    def forward(self, rotations=1.0, speed_pct=None):
        """Drive forward normally."""
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception:
                pass

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
        """Drive backward normally."""
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception:
                pass

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
        """Turn robot left in place by X degrees (approx)."""
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception:
                pass
        print("Turning left %d°..." % degrees)
        # Adjust scaling if your turn radius differs
        turn_rot = degrees / 90.0 * 0.5  # tweak factor for calibration
        try:
            self.left.spin_for(REVERSE, turn_rot, TURNS, False)
            self.right.spin_for(FORWARD, turn_rot, TURNS, True)
        except Exception:
            self.left.spin(REVERSE)
            self.right.spin(FORWARD)
            wait(800, MSEC)
        self._stop()

    def turn_right(self, degrees=90, speed_pct=None):
        """Turn robot right in place by X degrees (approx)."""
        if speed_pct is not None:
            try:
                self.left.set_velocity(int(speed_pct), PERCENT)
                self.right.set_velocity(int(speed_pct), PERCENT)
            except Exception:
                pass
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

    def status(self):
        try:
            lp = self.left.position(DEGREES)
            rp = self.right.position(DEGREES)
            print("%s: L=%s°, R=%s°" % (self.name, str(lp), str(rp)))
        except Exception:
            pass

class ClawMotor:
    """
    Claw motor that closes until stall and opens for a timed duration.
    Simple to use: claw.close() and claw.open()
    """
    def __init__(self, port_number, name="Claw", speed_pct=40, reversed=False, backoff_deg=6):
        if port_number not in PORT_MAP:
            raise ValueError("Invalid port number: %d" % port_number)

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
        """Close claw until stall detected, then back off slightly."""
        print("Closing claw...")
        try:
            self.m.spin(REVERSE)  # REVERSE = close direction (flip if needed)
        except Exception:
            return

        step = 20
        elapsed = 0
        still_elapsed = 0
        last_pos = self._pos()

        while elapsed < timeout_ms:
            pos = self._pos()
            vel = self._vel()

            moved = pos is not None and last_pos is not None and abs(pos - last_pos) > 0.15
            if moved:
                still_elapsed = 0
            else:
                if vel is None or abs(vel) < 1:
                    still_elapsed += step

            if still_elapsed >= 350:  # stalled for 350ms
                break

            last_pos = pos
            wait(step, MSEC)
            elapsed += step

        self._stop()

        # backoff to relieve pressure
        if self.backoff_deg > 0:
            try:
                self.m.spin_for(self.backoff_deg, DEGREES, True)
            except Exception:
                self.m.spin(FORWARD)
                wait(120, MSEC)
                self._stop()

        print("Claw closed. pos=%s°" % str(self._pos()))

    def open(self, ms=600, speed_pct=None):
        """Open claw for a short duration."""
        if speed_pct is not None:
            try: self.m.set_velocity(int(speed_pct), PERCENT)
            except Exception: pass

        print("Opening claw...")
        try:
            self.m.spin(FORWARD)
            wait(int(ms), MSEC)
        finally:
            self._stop()

        print("Claw opened. pos=%s°" % str(self._pos()))


def test_claw(claw):
    print("\nOpening claw...")
    claw.open()

    print("\Closing claw...")
    claw.close()

# ---------------------------
# Example usage
# ---------------------------
def main():
    print_leopard()

    print("Brain connected. Battery: %d %%" % brain.battery.capacity())

    claw = ClawMotor(port_number=9, name="Claw", speed_pct=60, reversed=False)
    test_claw(claw)
   
    drive = DriveMotor(left_port=12, right_port=11, default_speed_pct=50)

    drive.forward(rotations=2)
    wait(300, MSEC)

    drive.turn_left(degrees=20)
    wait(300, MSEC)

main()



