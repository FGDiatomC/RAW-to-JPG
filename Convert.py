import streamlit as st
from PIL import Image
import rawpy
import io
import zipfile

def convert_nef_to_jpg(nef_file):
    # Open the NEF file using rawpy
    with rawpy.imread(nef_file) as raw:
        # Convert to RGB
        rgb_image = raw.postprocess()
    
    # Convert RGB image to PIL image
    pil_image = Image.fromarray(rgb_image)
    return pil_image

# Initialize session state for uploaded files
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None

# Streamlit app
st.title("NEF to JPG Converter")

st.write("Upload your .NEF files and convert them to high-quality .JPG.")

# File uploader for NEF files
uploaded_files = st.file_uploader("Choose .NEF files", type=["nef"], accept_multiple_files=True)

# Store uploaded files in session state
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

# Display convert button only if files are uploaded
if st.session_state.uploaded_files:
    if st.button("Convert Images"):
        # Initialize progress bar
        progress_bar = st.progress(0)
        total_files = len(st.session_state.uploaded_files)

        if total_files == 1:
            # Single file conversion
            nef_file = st.session_state.uploaded_files[0]
            jpg_image = convert_nef_to_jpg(nef_file)

            # Save the converted image to a BytesIO buffer
            buf = io.BytesIO()
            jpg_image.save(buf, format="JPEG", quality=100)
            byte_im = buf.getvalue()

            # Update progress bar to 100%
            progress_bar.progress(100)

            # Display download button for the converted JPG image
            st.download_button(
                label="Download JPG",
                data=byte_im,
                file_name=f"{nef_file.name.split('.')[0]}.jpg",
                mime="image/jpeg"
            )

        else:
            # Multiple files conversion
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for idx, nef_file in enumerate(st.session_state.uploaded_files):
                    jpg_image = convert_nef_to_jpg(nef_file)

                    # Save the converted image to a BytesIO buffer
                    img_buffer = io.BytesIO()
                    jpg_image.save(img_buffer, format="JPEG", quality=100)
                    byte_im = img_buffer.getvalue()

                    # Add each image to the zip file
                    zip_file.writestr(f"{nef_file.name.split('.')[0]}.jpg", byte_im)

                    # Update progress bar
                    progress_percentage = int(((idx + 1) / total_files) * 100)
                    progress_bar.progress(progress_percentage)

            # Move the cursor of the BytesIO object to the beginning
            zip_buffer.seek(0)

            # Display download button for the zip file containing all converted images
            st.download_button(
                label="Download All as ZIP",
                data=zip_buffer,
                file_name="converted_images.zip",
                mime="application/zip"
            )

        # Conversion completed
        st.success("Conversion completed successfully!")

        # Clear uploaded files after conversion is completed
        st.session_state.uploaded_files = None