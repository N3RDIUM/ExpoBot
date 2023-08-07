from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import glfw
from text import text, display_debug
import noise
import random

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

player = Player()
amplitude_samples = []
_amplitude_samples = []
smooth_amplitude = 0
dots = []
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
    if frames_listening == 0:
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
            if len(amplitude_samples) > 32:
                amplitude_samples.pop(0)
            if len(_amplitude_samples) > 8:
                _amplitude_samples.pop(0)
            smooth_amplitude = sum(_amplitude_samples) / len(_amplitude_samples)
            amplitude_samples.append(smooth_amplitude)
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
    else:
        text((10, 10), "Waiting for server " + get_spinner())
    
    # Draw the 3D scene
    _setup_3d()
    glClearColor(
        0.1 + noise.pnoise1(_frame / 800 + 64) / 4 + frames_listening / 60,
        0.1 + noise.pnoise1(_frame / 800 + 32) / 4 + frames_listening / 60,
        0.1 + noise.pnoise1(_frame / 800 + 16) / 4 + frames_listening / 60,
        1
    )
    # player.update(window)
    if server:
        _frame += smooth_amplitude / 32
        sphere((0, 0, -10), (smooth_amplitude + noise.pnoise1(_frame / 200 - 400)*50) / 1024 + 0.24, (
            min(1 - (noise.pnoise1(_frame / 100) + frames_listening / 60), 1),
            min(1 - (noise.pnoise1(_frame / 100-200) + frames_listening / 60), 1),
            min(1 - (noise.pnoise1(_frame / 100-300) + frames_listening / 60), 1),
        ))
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
        sphere((0, 0, -20), (a1 + noise.pnoise1(_frame / 200 - 1000)*80) / 1024 + 1.24, (
            123/255 + noise.pnoise1(_frame / 100) / 4,
            213/255 + noise.pnoise1(_frame / 100 + 100) / 4,
            252/255 + noise.pnoise1(_frame / 100 + 200) / 4,
        ))
        sphere((0, 0, -40), (a2 + noise.pnoise1(_frame / 200 - 2000)*100) / 1024 + 3.24, (
            7/255 + noise.pnoise1(_frame / 100 + 300) / 4,
            178/255 + noise.pnoise1(_frame / 100 + 400) / 4,
            252/255 + noise.pnoise1(_frame / 100 + 500) / 4,
        ))
        sphere((0, 0, -80), (a3 + noise.pnoise1(_frame / 200 - 4000)*256) / 1024 + 8.24, (
            1/255 + noise.pnoise1(_frame / 100 + 600) / 4,
            130/255 + noise.pnoise1(_frame / 100 + 700) / 4,
            186/255 + noise.pnoise1(_frame / 100 + 800) / 4,
        ))
    
            
    # Keep running
    glfw.poll_events()
    glfw.swap_buffers(window)

# Cleanup
glfw.terminate()
if server:
    server.thread.join()