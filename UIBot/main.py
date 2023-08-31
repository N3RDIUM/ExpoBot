from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import glfw
from text import text, display_debug
import noise
import numpy as np
import subprocess
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "../Chatbot/main.py")])
subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "../Feedback/main.py")])

from server import Server
from player import Player

if not glfw.init():
    raise Exception("glfw could not be initialized!")
window = glfw.create_window(640, 480, "Hello World", None, None)
glfw.show_window(window)
glfw.make_context_current(window)
server_start = False
server = None
spinner = ["|", "/", "-", "\\"]
spinner_index = 0
frame = 0
_frame = 0
def get_spinner():
    global spinner_index
    if frame % 10 == 0:
        spinner_index += 1
        if spinner_index >= len(spinner):
            spinner_index = 0
    return spinner[spinner_index]

def _setup_3d():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, *glfw.get_window_size(window))
    window_size = glfw.get_window_size(window)
    gluPerspective(45, window_size[0] / window_size[1], 0.1, 100000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    
def _setup_2d():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 640, 480, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    
def enable_antialiasing():
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    
def sphere(pos, radius, color):
    glPushMatrix()
    glTranslatef(*pos)
    glColor3f(*color)
    glutSolidSphere(radius, 100, 100)
    glPopMatrix()
    
def point(pos, size, color):
    glPushMatrix()
    glTranslatef(*pos)
    glColor3f(*color)
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()
    glPopMatrix()
    
def getsample(samples, i, j):
    try:
        return samples[i*len(samples)//len(dots)][j*len(samples)//len(dots[i])]
    except:
        return 0

player = Player()
amplitude_samples = []
amplitude_samples_large = []
_amplitude_samples = []
smooth_amplitude = 0
downscale = 1
dots = np.zeros((100 // downscale, 50 // downscale, 1))
dot_vbo = glGenBuffers(1)
dot_vbo_data = []
# Persistently map the buffer
frames_listening = 0

# Main loop
while not glfw.window_should_close(window):
    frame += 1
    _frame += 1
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 1)
    enable_antialiasing()
    
    _setup_2d()
    if not server_start:
        server_start = True
        server = Server()
    
    # TODO: Constantly update the server with the mic amplitude
    if frames_listening <= 0:
        glColor3f(1, 1, 1)
    else:
        glColor3f(0, 0, 0)
    if server:
        if not server.initialized: 
            text((10, 10), "Initializing server " + get_spinner())
        if server.initialized and not server.connected:
            text((10, 10), "Waiting for client " + get_spinner())
        if server.connected:
            _amplitude_samples.append(server.data["amplitude"])
            if len(amplitude_samples) > 16:
                amplitude_samples.pop(0)
            if len(_amplitude_samples) > 8:
                _amplitude_samples.pop(0)
            smooth_amplitude = sum(_amplitude_samples) / len(_amplitude_samples)
            amplitude_samples.append(smooth_amplitude)
            
            amplitude_samples_large.append(server.data["amplitude"])
            if len(amplitude_samples_large) > 512:
                amplitude_samples_large.pop(0)

            text((10, 10), "Connected to client")
            display_debug((10, 20), [
                "Amplitude: " + str(server.data["amplitude"]),
                "Speaking: " + server.data["speaking"],
                "User text: " + server.data["user-text"],
                "Speaking text: " + server.data["speaking-text"]
            ])
            if bool(server.data["listening"]):
                frames_listening += 1
            else:
                frames_listening -= 8
            if frames_listening < 0:
                frames_listening = 0
            if frames_listening > 60:
                frames_listening = 60
    else:
        text((10, 10), "Waiting for server " + get_spinner())
    
    # Draw the 3D scene
    _setup_3d()
    glClearColor(
        0.1 + noise.pnoise1(_frame / 800 + 64) / 8 + frames_listening / 60,
        0.1 + noise.pnoise1(_frame / 800 + 32) / 8 + frames_listening / 60,
        0.1 + noise.pnoise1(_frame / 800 + 16) / 8 + frames_listening / 60,
        1
    )
    # player.update(window)
    if server:
        try:
            _frame += 1 + abs(smooth_amplitude - sum(amplitude_samples_large) / len(amplitude_samples_large)) / 16
        except: _frame += 1
        a1 = 0
        try:
            a1 = amplitude_samples[len(amplitude_samples) // 4]
        except: pass   
        
        a2 = 0
        try:
            a2 = amplitude_samples[len(amplitude_samples) // 2]
        except: pass
        
        a3 = 0
        try:
            a3 = amplitude_samples[len(amplitude_samples) // 4 * 3]
        except: pass
        sphere((0, 0, -10), (smooth_amplitude*2 + noise.pnoise1(_frame / 200 - 400)*50) / 1024 + 0.24, (
            min(1 - (noise.pnoise1(_frame / 100) + frames_listening / 60), 1),
            min(1 - (noise.pnoise1(_frame / 100-200) + frames_listening / 60), 1),
            min(1 - (noise.pnoise1(_frame / 100-300) + frames_listening / 60), 1),
        ))
        sphere((0, 0, -20), (a3*5 + noise.pnoise1(_frame / 200 - 1000)*80) / 1024 + 1.24, (
            123/255 + noise.pnoise1(_frame / 100) / 4,
            213/255 + noise.pnoise1(_frame / 100 + 100) / 4,
            252/255 + noise.pnoise1(_frame / 100 + 200) / 4,
        ))
        sphere((0, 0, -40), (a2*5 + noise.pnoise1(_frame / 200 - 2000)*100) / 1024 + 4.24, (
            7/255 + noise.pnoise1(_frame / 100 + 300) / 4,
            178/255 + noise.pnoise1(_frame / 100 + 400) / 4,
            252/255 + noise.pnoise1(_frame / 100 + 500) / 4,
        ))
        sphere((0, 0, -80), (a1*5 + noise.pnoise1(_frame / 200 - 4000)*256) / 1024 + 10.24, (
            1/255 + noise.pnoise1(_frame / 100 + 600) / 4,
            130/255 + noise.pnoise1(_frame / 100 + 700) / 4,
            186/255 + noise.pnoise1(_frame / 100 + 800) / 4,
        ))
    
    # Draw dots as spheres in the bg, the third index is the radius
    for i in range(len(dots)):
        for j in range(len(dots[i])):
            # Update dot sizes according to amplitude and noise
            dots[i][j][0] = (getsample(amplitude_samples_large, i, j) * 1600 + abs(noise.pnoise1((_frame - i*j)/512)) * 25) + 0.1
            # Update dot colors according to noise
            color = (
                min(1 - (noise.pnoise1((_frame - i*j) / 100-100) + frames_listening / 60), 1),
                min(1 - (noise.pnoise1((_frame - i*j) / 100-200) + frames_listening / 60), 1),
                min(1 - (noise.pnoise1((_frame - i*j) / 100-300) + frames_listening / 60), 1),
            )
            # Draw the dot
            x = i * 2 - len(dots) + 1
            y = j * 2 - len(dots[i]) + 1
            point((
                x * downscale - noise.pnoise1((_frame - i*j) / 100) / 2 + noise.pnoise1((_frame + i*j) / 200 + 200) / 2, 
                y * downscale - noise.pnoise1((_frame - i*j) / 100 + 100) / 2 + noise.pnoise1((_frame + i*j) / 200 + 300) / 2,
            -100), dots[i][j][0], color=color)
    # Keep running
    glfw.poll_events()
    glfw.swap_buffers(window)

# Cleanup
glfw.terminate()
if server:
    server.thread.join()