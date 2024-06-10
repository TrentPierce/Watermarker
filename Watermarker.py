import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import cv2
import os
import threading

def select_file():
    file_path = filedialog.askopenfilename()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def add_watermark():
    file_path = file_entry.get()
    watermark_text = watermark_entry.get()
    
    if not file_path or not watermark_text:
        messagebox.showerror("Error", "Please select a file and enter the watermark text.")
        return
    
    loading_label = tk.Label(root, text="Processing... Please wait")
    loading_label.grid(row=3, column=0, columnspan=3)
    
    loading_thread = threading.Thread(target=process_file, args=(file_path, watermark_text, loading_label))
    loading_thread.start()

def process_file(file_path, watermark_text, loading_label):
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            process_image(file_path, watermark_text)
        elif file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
            progress_bar = tk.Canvas(root, width=300, height=20)
            progress_bar.grid(row=4, column=0, columnspan=3, pady=10)
            progress_bar.create_rectangle(0, 0, 0, 20, fill="blue")
            progress_bar.update()
            
            process_video(file_path, watermark_text, loading_label, progress_bar)
        else:
            messagebox.showerror("Error", "Unsupported file type.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add watermark: {e}")
    finally:
        loading_label.destroy()

def process_image(image_path, watermark_text):
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 36)
        
        width, height = image.size
        
        # Get text size
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = width - text_width - 10
        y = height - text_height - 10
        
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
        
        output_path = os.path.join(os.path.dirname(image_path), "watermarked_" + os.path.basename(image_path))
        image.save(output_path)
        
        show_success_message(output_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add watermark: {e}")

def process_video(video_path, watermark_text, loading_label, progress_bar):
    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the codec
        output_path = os.path.join(os.path.dirname(video_path), "watermarked_" + os.path.basename(video_path))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (50, 50)
        fontScale = 1
        color = (255, 255, 255)
        thickness = 2
        
        for frame_no in range(total_frames):
            ret, frame = video.read()
            if not ret:
                break
            
            cv2.putText(frame, watermark_text, org, font, fontScale, color, thickness, cv2.LINE_AA)
            out.write(frame)
            
            progress_width = (frame_no + 1) * 300 / total_frames
            progress_bar.create_rectangle(0, 0, progress_width, 20, fill="blue")
            progress_bar.update()
            
        video.release()
        out.release()
        
        show_success_message(output_path, progress_bar)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add watermark: {e}")

def show_success_message(output_path, progress_bar=None):
    messagebox.showinfo("Success", f"Watermarked file saved as {output_path}")
    if progress_bar:
        progress_bar.destroy()

# Set up the Tkinter window
root = tk.Tk()
root.title("Watermarker")
root.iconbitmap("watermarker.ico")

# File selection
tk.Label(root, text="Select File:").grid(row=0, column=0, padx=10, pady=10)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)
file_button = tk.Button(root, text="Browse", command=select_file)
file_button.grid(row=0, column=2, padx=10, pady=10)

# Watermark text input
tk.Label(root, text="Watermark Text:").grid(row=1, column=0, padx=10, pady=10)
watermark_entry = tk.Entry(root, width=50)
watermark_entry.grid(row=1, column=1, padx=10, pady=10)

# Add watermark button
add_button = tk.Button(root, text="Add Watermark", command=add_watermark)
add_button.grid(row=2, column=0, columnspan=3, pady=10)

# Run the Tkinter event loop
root.mainloop()
