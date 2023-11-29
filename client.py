import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import socket
from datetime import datetime
from threading import Thread
from tkinter import filedialog
import io
import cv2
class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 9999))

        self.root = tk.Tk()
        self.root.title("Client")
        self.root.geometry("450x600")
        self.root.configure(bg="#b39e6f")  # Set background color to WhatsApp-like color
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.chat_area = tk.Text(self.root, bg="#baa063", fg="black", font=("Arial", 12), padx=10, pady=10)  # Set background color to WhatsApp-like color
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        self.message_entry = tk.Entry(self.root, font=("Arial", 12),
                                      bg="#f5f5f5")  # Set background color to WhatsApp-like color
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        send_button = tk.Button(self.root, text="Text", command=self.send_message, bg="#075e54", fg="white", bd=0,
                                relief=tk.RAISED, padx=8, pady=8, borderwidth=0, highlightthickness=0,
                                highlightbackground="#075e54")
        send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        send_file_button = tk.Button(self.root, text="File", command=self.send_file, bg="#075e54", fg="white",
                                     bd=0, relief=tk.RAISED, padx=8, pady=8, borderwidth=0, highlightthickness=0,
                                     highlightbackground="#075e54")
        send_file_button.pack(side=tk.RIGHT, padx=5, pady=5)

        image_button = tk.Button(self.root, text="Image", command=self.send_image, bg="#075e54", fg="white", bd=0,
                                 relief=tk.RAISED, padx=8, pady=8, borderwidth=0, highlightthickness=0,
                                 highlightbackground="#075e54")
        image_button.pack(side=tk.RIGHT, padx=5, pady=5)

        video_button = tk.Button(self.root, text="Video", command=self.send_video, bg="#075e54", fg="white", bd=0,
                                 relief=tk.RAISED, padx=8, pady=8, borderwidth=0, highlightthickness=0,
                                 highlightbackground="#075e54")
        video_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.receive_thread = Thread(target=self.receive_messages)
        self.receive_thread.start()

        self.root.mainloop()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.client_socket.send(message.encode("UTF-8"))
            self.display_message("You", message, "#e0e0e0",
                                 "right")  # Display sent message on the right side with light grey background
            self.message_entry.delete(0, tk.END)

    def send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "r") as file:
                file_data = file.read()
                file_name = file.name.split("/")[-1]
                self.client_socket.send(f"FILE {file_name}".encode("UTF-8"))
                self.client_socket.send(file_data.encode("UTF-8"))
            self.display_message("You", f"File Sent: {file_name}", "#e0e0e0", "right")  # Display sent file message on the right side with light grey background

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("UTF-8")
                if message.startswith("FILE "):
                    file_name = "File_from_Server.txt"
                    # file_data = self.client_socket.recv(1024)
                    with open(file_name, "w") as file:
                        data = self.client_socket.recv(262144).decode('UTF-8')
                        file.write(data)
                    self.display_message("Server", f"File Received: {file_name}", "#dcf8c6", "left")  # Display received file message on the left side with light green background
                elif message == "IMAGE":
                    file = open("Image_from_Server.jpg", "wb")
                    image_chunk = self.client_socket.recv(262144)
                    file.write(image_chunk)
                    file.close()
                    image_path = "D:\S-6\Instant_messaging_CN_Project\Image_from_Server.jpg"
                    self.display_message("Server", "Image Received", "#dcf8c6", "left")
                    self.display_received_image("Client", image_path)
                elif message == "VIDEO":
                    self.client_socket.settimeout(10)
                    try:
                        file_name = "D:\S-6\Instant_messaging_CN_Project\Video_from_Server.jpg"
                        with open(file_name, 'wb') as file:
                            counter = 1
                            data = io.BytesIO()
                            while True:
                                data = self.client_socket.recv(262144)
                                file.write(data)
                                print(counter)
                                counter = counter + 1
                    except socket.timeout:
                        self.display_message("Server", "Video Received", "#dcf8c6", "left")
                        self.display_received_video("You", file_name, "#e0e0e0", "right")

                elif message:
                    self.display_message("Server", message, "#dcf8c6", "left")  # Display received message on the left side with light green background
            except Exception as e:
                print(str(e))
                break

    def display_message(self, sender, message, bg_color, align):
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: {message}\n"
        self.chat_area.tag_configure(sender, background=bg_color)  # Configure the tag with the background color
        self.chat_area.insert(tk.END, formatted_message, sender)  # Apply the tag to the message
        self.chat_area.tag_configure(sender, justify=align)  # Set the alignment of the message
        self.chat_area.yview(tk.END)

    def send_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            resized_image = image.resize((200, 200))
            self.image_data = ImageTk.PhotoImage(resized_image)  # Assign to instance variable
            # cpimage= self.image_data.copy()

            self.client_socket.send("IMAGE".encode("UTF-8"))

            # Save image data to a file-like object
            image_file = io.BytesIO()
            resized_image.save(image_file, format="JPEG")

            # Get the contents of the file-like object and send over the socket
            image_bytes = image_file.getvalue()
            self.client_socket.sendall(image_bytes)

            self.display_sent_image("You", self.image_data, "#e0e0e0", "right")  # Display sent image on the right side with light grey background

    def send_video(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.display_message("You", "", "#e0e0e0", "right")
            with open(file_path, 'rb') as video_file:
                self.client_socket.send("VIDEO".encode("UTF-8"))
                video_data = video_file.read()
                self.client_socket.sendall(video_data)
                self.display_sent_video("You", file_path, "#e0e0e0", "right")

    def display_sent_video(self, sender, file, bg_color, align):
        video = cv2.VideoCapture(file)
        success, frame = video.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(frame_rgb, (200, 200))
        image = Image.fromarray(resized_frame)
        image_tk = ImageTk.PhotoImage(image)
        self.chat_area.insert(tk.END, " " * 50)  # Add empty spaces for alignment
        self.chat_area.image_create(tk.END, image=image_tk)
        self.chat_area.insert(tk.END, '\n')  # Add a newline after the image
        self.chat_area.insert(tk.END, "\n")  # Insert a new line after the image
        self.chat_area.yview(tk.END)
        # Keep a reference to the PhotoImage object to avoid garbage collection
        self.chat_area.image = image_tk

    def display_received_video(self, sender, file, bg_color, align):
        video = cv2.VideoCapture(file)
        success, frame = video.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(frame_rgb, (200, 200))
        image = Image.fromarray(resized_frame)
        image_tk = ImageTk.PhotoImage(image)
        self.chat_area.image_create(tk.END, image=image_tk)
        self.chat_area.insert(tk.END, '\n')  # Add a newline after the image
        self.chat_area.insert(tk.END, "\n")  # Insert a new line after the image
        self.chat_area.yview(tk.END)
        # Keep a reference to the PhotoImage object to avoid garbage collection
        self.chat_area.image = image_tk

    def display_sent_image(self, sender, image_data, bg_color, align):
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: \n"
        self.chat_area.tag_configure(sender, background=bg_color)  # Configure the tag with the background color
        self.chat_area.insert(tk.END, formatted_message, sender)  # Apply the tag to the message
        self.chat_area.tag_configure(sender, justify="right")  # Set the alignment of the message
        self.chat_area.insert(tk.END, " " * 50)  # Add empty spaces for alignment
        self.chat_area.image_create(tk.END, image=self.image_data)
        self.chat_area.insert(tk.END, "\n")  # Insert a new line after the image
        self.chat_area.yview(tk.END)

    def display_received_image(self, sender, image_path):
        # Resize the image to fit the chatbox
        image = Image.open(image_path)
        max_width = 200
        max_height = 200
        image = image.resize((max_width, max_height))

        # Create a Tkinter PhotoImage object from the PIL Image object
        photo = ImageTk.PhotoImage(image)

        # Insert the image into the chat area
        self.chat_area.image_create(tk.END, image=photo)
        self.chat_area.insert(tk.END, '\n')  # Add a newline after the image
        self.chat_area.insert(tk.END, "\n")  # Insert a new line after the image
        self.chat_area.yview(tk.END)
        # Keep a reference to the PhotoImage object to avoid garbage collection
        self.chat_area.image = photo


    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.client_socket.close()
            self.receive_thread.join()
            self.root.destroy()

if __name__ == "__main__":
    client = Client()