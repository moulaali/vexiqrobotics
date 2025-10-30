from vex import *


brain = Brain()
print("Brain connected. Battery:", brain.battery.capacity(), "%")

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

# ------------------ Helper method ------------------
def detect_classroom_objects(sensor):
    """
    Detect and print objects recognized by the 'Classroom Objects' AI model.
    Returns a list of dictionaries for reuse.
    """
    objs = sensor.take_snapshot(AiVision.ALL_AIOBJS)
    if not objs and len(getattr(sensor, "objects", [])) == 0:
        print("No classroom objects detected.")
        return []

    try:
        label_map = {
            GameElementsClassroomObjects.BALL: "BALL",
            GameElementsClassroomObjects.CUBE: "CUBE",
            GameElementsClassroomObjects.CONE: "CONE",
            GameElementsClassroomObjects.CYLINDER: "CYLINDER",
            GameElementsClassroomObjects.PERSON: "PERSON",
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

# --- Main Loop ---
print("Scanning Mix & Match AI objects… (Press Stop on Brain to end)")
while True:
    detect_classroom_objects(vs)
    wait(500, MSEC)
