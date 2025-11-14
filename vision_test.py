#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

# Brain should be defined by default
brain=Brain()

# Robot configuration code
brain_inertial = Inertial()
# AI Classification Competition Element IDs - Mix & Match
class GameElementsMixAndMatch:
    BEAM = 0
    BLUE_PIN = 1
    RED_PIN = 2
    ORANGE_PIN = 3
# AI Vision Color Descriptions
# AI Vision Code Descriptions
ai_vision_1 = AiVision(Ports.PORT1, AiVision.ALL_AIOBJS)



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

def scan_objects(max_count=8):
    """
    Reads objects from the configured AI Vision sensor (ai_vision_1)
    and prints readable Mix & Match labels.

    Returns a list of dicts:
    {id, label, centerX, centerY, width, height, area}
    """

    # Mix & Match default model IDs
    LABELS = {
        0: "BEAM",
        1: "BLUE PIN",
        2: "RED PIN",
        3: "ORANGE PIN",
        # Some firmware versions use 4/5 for confidence/meta objects
        4: "UNKNOWN",
        5: "UNKNOWN"
    }

    results = []

    # TAKE SNAPSHOT
    objs = ai_vision_1.take_snapshot(AiVision.ALL_AIOBJS)

    # If nothing returned
    if not objs:
        print("No objects detected.")
        return []

    print("\n=== DETECTED OBJECTS ===")

    # Loop through objects
    count = 0
    for o in objs:
        if count >= max_count:
            break
        count += 1

        # Safely extract fields
        try:
            obj_id = int(getattr(o, "id", -1))
            cx = int(getattr(o, "centerX", 0))
            cy = int(getattr(o, "centerY", 0))
            w = int(getattr(o, "width", 0))
            h = int(getattr(o, "height", 0))

            label = LABELS.get(obj_id, "UNKNOWN")
            area = w * h

            print("%s (id=%d) | center=(%d,%d) | size=%dx%d | area=%d" %
                  (label, obj_id, cx, cy, w, h, area))

            results.append({
                "id": obj_id,
                "label": label,
                "centerX": cx,
                "centerY": cy,
                "width": w,
                "height": h,
                "area": area
            })

        except Exception as e:
            print("[ERROR] Failed to decode object:", e)

    print("=========================\n")
    return results



while True:
    scan_objects()
    wait(1000, MSEC)

