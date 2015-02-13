# TouchWizard

This project aims at easing GUI development for touchscreens by using an info/widget/icon vertical canvas developped in clutter (using the python bindings).

## Concepts

### InfoBar

Label which listens to the "info" event. Any element launching an "info" signal with text as event contents will have the text displayed in the box.

### WidgetsArea

Generic area for displaying regular clutter widgets. It should implement some form of layout mechanism.

### IconBar

Icon handling area; icons can either be :
  * ActionIcon: icon which sends an event
  * ToggleIcon: two-states (on/off) icon

Icon states are:
  * normal (ready)
  * locked (unavailable)
  * cooldown (waiting for a few seconds before allowing a new call)
  * active (currently unimplemented)

An icon behaviour is defined by passing to the constructor:
  * "launch_evt": the event type it will launch once pressed
  * "listen_evt": will make the icon react to external events
  * "file": icon file prefix from the icons/ directory (png file)
  * "cooldown_ms": duration in milliseconds for the action to be callable again

Additionally, ToggleIcon can lock all the other icons in the bar by passing the "locks_others" boolean.
