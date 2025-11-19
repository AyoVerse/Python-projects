import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import threading

class ComicTextRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("Comic Book Speech Bubble Text Remover")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.images = []
        self.current_index = 0
        self.processed_images = []
        self.output_dir = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Comic Book Speech Bubble Text Remover", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Upload button
        upload_btn = ttk.Button(main_frame, text="Upload Images", command=self.upload_images)
        upload_btn.grid(row=1, column=0, padx=(0, 10), pady=10, sticky=tk.W)
        
        # Output directory button
        output_btn = ttk.Button(main_frame, text="Select Output Directory", command=self.select_output_dir)
        output_btn.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Process button
        process_btn = ttk.Button(main_frame, text="Process All Images", command=self.process_all_images)
        process_btn.grid(row=1, column=2, padx=(10, 0), pady=10, sticky=tk.W)
        
        # Image display frame
        display_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding="10")
        display_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.canvas = tk.Canvas(display_frame, bg="white", width=800, height=400)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Navigation frame
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Previous button
        self.prev_btn = ttk.Button(nav_frame, text="Previous", command=self.previous_image, state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=0, padx=5)
        
        # Next button
        self.next_btn = ttk.Button(nav_frame, text="Next", command=self.next_image, state=tk.DISABLED)
        self.next_btn.grid(row=0, column=1, padx=5)
        
        # Save current button
        self.save_btn = ttk.Button(nav_frame, text="Save Current", command=self.save_current_image, state=tk.DISABLED)
        self.save_btn.grid(row=0, column=2, padx=5)
        
        # Save all button
        self.save_all_btn = ttk.Button(nav_frame, text="Save All Processed", command=self.save_all_images, state=tk.DISABLED)
        self.save_all_btn.grid(row=0, column=3, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Please upload images to begin")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
    def upload_images(self):
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Select Comic Book Images", filetypes=file_types)
        
        if files:
            self.images = list(files)
            self.current_index = 0
            self.processed_images = [None] * len(self.images)
            
            # Enable navigation buttons if we have images
            if len(self.images) > 0:
                self.next_btn.config(state=tk.NORMAL)
                self.prev_btn.config(state=tk.NORMAL)
                self.save_all_btn.config(state=tk.NORMAL)
                self.display_current_image()
                self.status_label.config(text=f"Loaded {len(self.images)} images. Click 'Process All Images' to remove text.")
            else:
                self.status_label.config(text="No images selected.")
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.status_label.config(text=f"Output directory: {directory}")
    
    def display_current_image(self):
        if not self.images or self.current_index >= len(self.images):
            return
            
        # Load and display the current image
        image_path = self.images[self.current_index]
        img = cv2.imread(image_path)
        
        if img is not None:
            # Convert BGR to RGB for display
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize for display while maintaining aspect ratio
            display_img = self.resize_for_display(img_rgb, max_width=800, max_height=400)
            
            # Convert to PhotoImage
            pil_img = Image.fromarray(display_img)
            self.tk_img = ImageTk.PhotoImage(pil_img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(400, 200, image=self.tk_img)
            
            # Update status
            self.status_label.config(text=f"Image {self.current_index + 1} of {len(self.images)}: {os.path.basename(image_path)}")
            
            # If this image has been processed, enable save button
            if self.processed_images[self.current_index] is not None:
                self.save_btn.config(state=tk.NORMAL)
            else:
                self.save_btn.config(state=tk.DISABLED)
    
    def resize_for_display(self, img, max_width, max_height):
        h, w = img.shape[:2]
        
        # Calculate scaling factor
        scale = min(max_width / w, max_height / h, 1.0)
        
        if scale < 1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(img, (new_w, new_h))
        else:
            return img
    
    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()
    
    def next_image(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.display_current_image()
    
    def process_all_images(self):
        if not self.images:
            messagebox.showwarning("Warning", "Please upload images first.")
            return
            
        if not self.output_dir:
            messagebox.showwarning("Warning", "Please select an output directory first.")
            return
            
        # Disable buttons during processing
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.save_all_btn.config(state=tk.DISABLED)
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_images_thread)
        thread.daemon = True
        thread.start()
    
    def process_images_thread(self):
        self.progress['value'] = 0
        self.progress['maximum'] = len(self.images)
        
        for i, image_path in enumerate(self.images):
            self.status_label.config(text=f"Processing image {i+1} of {len(self.images)}...")
            
            # Process the image
            processed_img = self.remove_text_from_image(image_path)
            self.processed_images[i] = processed_img
            
            # Update progress
            self.progress['value'] = i + 1
            self.root.update_idletasks()
        
        # Re-enable buttons
        self.prev_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.save_all_btn.config(state=tk.NORMAL)
        
        # Display the first processed image
        self.current_index = 0
        self.display_processed_image()
        
        self.status_label.config(text=f"Processing complete! {len(self.images)} images processed.")
        messagebox.showinfo("Success", f"All {len(self.images)} images have been processed successfully!")
    
    def remove_text_from_image(self, image_path):
        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # Create a copy of the original image
        result = img.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply multiple methods to detect text regions
        
        # Method 1: Using morphological operations to find text-like regions
        # Create a rectangular kernel for dilation
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Apply blackhat operation to find dark text on light background
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
        
        # Dilate to connect text components
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        # Method 2: Using edge detection to find contours that might be text
        edges = cv2.Canny(gray, 50, 150)
        
        # Combine both methods
        combined = cv2.bitwise_or(dilated, edges)
        
        # Find contours in the combined mask
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and aspect ratio to find text regions
        text_contours = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Filter based on area and aspect ratio (text tends to be wider than tall)
            if area > 50 and w > h and w < img.shape[1] * 0.8 and h < img.shape[0] * 0.8:
                text_contours.append(contour)
        
        # If we found text contours, apply inpainting to remove them
        if text_contours:
            # Create a mask for the text regions
            mask = np.zeros(gray.shape, np.uint8)
            cv2.drawContours(mask, text_contours, -1, 255, -1)
            
            # Apply inpainting to remove text while preserving the background
            result = cv2.inpaint(result, mask, 3, cv2.INPAINT_TELEA)
        
        return result
    
    def display_processed_image(self):
        if (self.processed_images and 
            self.current_index < len(self.processed_images) and 
            self.processed_images[self.current_index] is not None):
            
            # Get the processed image
            processed_img = self.processed_images[self.current_index]
            
            # Convert BGR to RGB for display
            img_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            display_img = self.resize_for_display(img_rgb, max_width=800, max_height=400)
            
            # Convert to PhotoImage
            pil_img = Image.fromarray(display_img)
            self.tk_img = ImageTk.PhotoImage(pil_img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(400, 200, image=self.tk_img)
            
            # Update status
            image_path = self.images[self.current_index]
            self.status_label.config(text=f"Processed image {self.current_index + 1} of {len(self.images)}: {os.path.basename(image_path)}")
    
    def save_current_image(self):
        if (self.processed_images and 
            self.current_index < len(self.processed_images) and 
            self.processed_images[self.current_index] is not None and
            self.output_dir):
            
            # Get the original filename
            original_path = self.images[self.current_index]
            filename = os.path.basename(original_path)
            name, ext = os.path.splitext(filename)
            
            # Create output path
            output_path = os.path.join(self.output_dir, f"{name}_no_text{ext}")
            
            # Save the processed image
            cv2.imwrite(output_path, self.processed_images[self.current_index])
            
            self.status_label.config(text=f"Saved: {output_path}")
            messagebox.showinfo("Success", f"Image saved as:\n{output_path}")
    
    def save_all_images(self):
        if not self.processed_images or not self.output_dir:
            messagebox.showwarning("Warning", "No processed images to save or output directory not selected.")
            return
        
        # Count how many images we'll save
        save_count = sum(1 for img in self.processed_images if img is not None)
        
        if save_count == 0:
            messagebox.showwarning("Warning", "No processed images to save.")
            return
        
        # Save all processed images
        saved_count = 0
        for i, processed_img in enumerate(self.processed_images):
            if processed_img is not None:
                # Get the original filename
                original_path = self.images[i]
                filename = os.path.basename(original_path)
                name, ext = os.path.splitext(filename)
                
                # Create output path
                output_path = os.path.join(self.output_dir, f"{name}_no_text{ext}")
                
                # Save the processed image
                cv2.imwrite(output_path, processed_img)
                saved_count += 1
        
        self.status_label.config(text=f"Saved {saved_count} images to: {self.output_dir}")
        messagebox.showinfo("Success", f"All {saved_count} processed images have been saved!")

def main():
    root = tk.Tk()
    app = ComicTextRemover(root)
    root.mainloop()

if __name__ == "__main__":
    main()