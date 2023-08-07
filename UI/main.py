from OpenGL.GL import *
import glfw
from text import text, display_debug

from server import Server

glfw.init()
window = glfw.create_window(640, 480, "Hello World", None, None)
glfw.show_window(window)
glfw.make_context_current(window)
server_start = False
server = None
spinner = ["|", "/", "-", "\\"]
spinner_index = 0
frame = 0
def get_spinner():
    global spinner_index
    if frame % 10 == 0:
        spinner_index += 1
        if spinner_index >= len(spinner):
            spinner_index = 0
    return spinner[spinner_index]
average_amplitude = 0
amplitude_samples = []

# Main loop
while not glfw.window_should_close(window):
    frame += 1
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0, 0, 0, 1)
    
    if not server_start:
        server_start = True
        server = Server()
    
    # TODO: Constantly update the server with the mic amplitude
    if server:
        if not server.initialized:    
            text((10, 10), "Initializing server " + get_spinner())
        if server.initialized and not server.connected:
            text((10, 10), "Waiting for client " + get_spinner())
        if server.connected:
            text((10, 10), "Connected to client")
            amplitude_samples.append(server.data["amplitude"])
            if len(amplitude_samples) > 1024:
                amplitude_samples.pop(0)
            average_amplitude = sum(amplitude_samples) / len(amplitude_samples)
            display_debug((10, 20), [
                "Amplitude: " + str(server.data["amplitude"]),
                "Average amplitude: " + str(average_amplitude),
                "Amplitude diff: " + str(server.data["amplitude"] - average_amplitude),
                "Speaking: " + server.data["speaking"],
                "User text: " + server.data["user-text"],
                "Speaking text: " + server.data["speaking-text"]
            ])
    else:
        text((10, 10), "Waiting for server " + get_spinner())
            
    # Keep running
    glfw.poll_events()
    glfw.swap_buffers(window)

# Cleanup
glfw.terminate()
if server:
    server.thread.join()