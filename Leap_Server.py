################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import socket

# //////////////////////// TCP socket creation ////////////////////////////////
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("127.0.0.1", 10015)
print 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(5)
connection = ''


class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        global connection
        try:
            # x = str(len(frame.hands)) + "\n"
            # connection.sendall(x.encode('ascii'))

            for hand in frame.hands:
                handType = "Left Hand" if hand.is_left else "Right Hand"
                normal = hand.palm_normal
                direction = hand.direction
                pitch = direction.pitch * Leap.RAD_TO_DEG  # Rotation around x-axis
                roll = normal.roll * Leap.RAD_TO_DEG  # Rotation around z-axis
                yaw = direction.yaw * Leap.RAD_TO_DEG  # Rotation around y-axis(Perpendicular to the plane)

                if pitch > 35:
                    connection.sendall((handType + ",Back\n").encode('ascii'))
                elif pitch < -35:
                    connection.sendall((handType + ",Front\n").encode('ascii'))

            for tool in frame.tools:
                connection.sendall(("Tool\n").encode('ascii'))

            for gesture in frame.gestures():
                # swipe gesture
                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = Leap.SwipeGesture(gesture)
                    swipe_id = swipe.id
                    swipe_state = self.state_names[gesture.state]
                    swipe_position = swipe.position
                    swipe_direction = swipe.direction
                    swipe_speed = swipe.speed
                    if swipe_direction.x > 0:
                        connection.sendall(("Swipe Right\n").encode('ascii'))
                    else:
                        connection.sendall(("Swipe Left\n").encode('ascii'))
                # screen tab gesture
                elif gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                    screentap = Leap.ScreenTapGesture(gesture)
                    screentap_id = gesture.id
                    screentap_state = self.state_names[gesture.state]
                    screentap_position = screentap.position
                    screentap_direction = screentap.direction
                    connection.sendall(("Screentab\n").encode('ascii'))

                # keytab Gesture
                elif gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                    keytap = Leap.KeyTapGesture(gesture)
                    keytap_id = gesture.id
                    keytap_state = self.state_names[gesture.state]
                    keytap_position = keytap.position
                    keytap_direction = keytap.direction
                    connection.sendall(("Keytab\n").encode('ascii'))

        except socket.error:
            create_connection()


def create_connection():
    print 'waiting for a connection'
    global connection
    connection, client_address = sock.accept()
    print 'connection from', client_address


def main():
    create_connection()
    time.sleep(5)
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()

    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
