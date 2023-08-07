from OpenGL.GL import *
import glfw
from math import sin, cos, radians, dist

class Player(object):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0]):
        self.position = position
        self.rotation = rotation
        self.mouse_prev = glfw.get_cursor_pos(glfw.get_current_context())
        self.speed = 2
    
    def update(self, window):
        # move forward
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1])) * 0.1 * self.speed
            self.position[2] += cos(radians(self.rotation[1])) * 0.1 * self.speed
            
        # move backward
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position[0] += sin(radians(self.rotation[1])) * 0.1 * self.speed
            self.position[2] -= cos(radians(self.rotation[1])) * 0.1 * self.speed
            
        # strafe left
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1] - 90)) * 0.1 * self.speed
            self.position[2] += cos(radians(self.rotation[1] - 90)) * 0.1 * self.speed
            
        # strafe right
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1] + 90)) * 0.1 * self.speed
            self.position[2] += cos(radians(self.rotation[1] + 90)) * 0.1 * self.speed
            
        # go up
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            self.position[1] -= 0.1 * self.speed
            
        # go down
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            self.position[1] += 0.1 * self.speed
        
        # drag mouse to rotate
        current_position = glfw.get_cursor_pos(window)
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            delta = []
            delta.append(current_position[0] - self.mouse_prev[0])
            delta.append(current_position[1] - self.mouse_prev[1])
            self.mouse_prev = current_position
        
            self.rotation[0] -= delta[1] * 0.1
            self.rotation[1] -= delta[0] * 0.1
            
            if self.rotation[0] > 90:
                self.rotation[0] = 90
            elif self.rotation[0] < -90:
                self.rotation[0] = -90
        self.mouse_prev = current_position
            
        # update view
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glTranslatef(self.position[0], self.position[1], self.position[2])