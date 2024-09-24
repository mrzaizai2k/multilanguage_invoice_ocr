import React, { useState, useCallback } from 'react';
import { Document, Page } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import { PhotoProvider, PhotoView } from 'react-photo-view';
import 'react-photo-view/dist/react-photo-view.css';
import axios from 'axios';
import './AddInvoice.css';

function AddInvoice() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [pdfPages, setPdfPages] = useState([]);
  const [images, setImages] = useState([]);
  const [rotation, setRotation] = useState(0);

  // Handle file selection for multiple files
  const handleFileChange = useCallback((event) => {
    const files = Array.from(event.target.files); // Handle multiple files
    const newImages = [];
    files.forEach((file) => {
      if (file.type === 'application/pdf') {
        const reader = new FileReader();
        reader.onload = function () {
          const pdfData = new Uint8Array(reader.result);
          processPdf(pdfData);
        };
        reader.readAsArrayBuffer(file);
      } else if (file.type.startsWith('image/')) {
        newImages.push(URL.createObjectURL(file));
      }
    });
    setImages((prevImages) => [...prevImages, ...newImages]); // Add new images to the list
    setSelectedFiles((prevFiles) => [...prevFiles, ...files]); // Store files for upload
  }, []);

  // Function to process PDF and extract pages as images
  const processPdf = async (pdfData) => {
    const pdf = await window.pdfjsLib.getDocument({ data: pdfData }).promise;
    const numPages = pdf.numPages;
    const pages = [];
    for (let i = 1; i <= numPages; i++) {
      const page = await pdf.getPage(i);
      const viewport = page.getViewport({ scale: 1 });
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      await page.render({ canvasContext: context, viewport: viewport }).promise;
      pages.push(canvas.toDataURL('image/png'));
    }
    setPdfPages((prevPages) => [...prevPages, ...pages]);
  };

  // Rotate selected image
  const rotateImage = () => {
    setRotation((prevRotation) => (prevRotation + 90) % 360);
  };

  // Upload each image to the server
  const handleUpload = async () => {
    if (!images.length && !pdfPages.length) {
      alert("Please select a file to upload.");
      return;
    }

    const filesToUpload = images.length ? images : pdfPages;

    for (const file of filesToUpload) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        await axios.post('/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        alert('File uploaded successfully');
      } catch (error) {
        console.error("Error uploading file:", error);
      }
    }
  };

  // Delete image from the preview
  const deleteImage = (imageToDelete) => {
    setImages((prevImages) => prevImages.filter((image) => image !== imageToDelete));
    setPdfPages((prevPages) => prevPages.filter((page) => page !== imageToDelete));
  };

  return (
    <div className="add-invoice">
      <div className="drop-zone">
        <div className="icon">↑</div>
        <p>Drag and drop your files here or</p>
        <input 
          type="file" 
          accept=".jpg,.png,.pdf" 
          multiple // Allow multiple file selection
          onChange={handleFileChange} 
        />
        <button className="browse-btn" onClick={handleUpload}>
          Upload Files
        </button>
        <div className="file-types">
          <span>JPG</span>
          <span>PNG</span>
          <span>PDF</span>
        </div>
      </div>

      {/* Show thumbnails of images */}
      <div className="thumbnail-container">
        <PhotoProvider
          toolbarRender={({ rotate, onRotate }) => {
            return (
              <svg
                className="PhotoView-Slider__toolbarIcon"
                onClick={() => onRotate(rotate + 90)}
                width="44"
                height="44"
                viewBox="0 0 768 768"
                fill="white"
              >
                <path d="M565.5 202.5l75-75v225h-225l103.5-103.5c-34.5-34.5-82.5-57-135-57-106.5 0-192 85.5-192 192s85.5 192 192 192c84 0 156-52.5 181.5-127.5h66c-28.5 111-127.5 192-247.5 192-141 0-255-114-255-255s114-255 255-255c70.5 0 135 28.5 181.5 72z" />
              </svg>
            );
          }}
        >
          {pdfPages.length > 0
            ? pdfPages.map((page, index) => (
                <div key={index} className="thumbnail-wrapper">
                  <PhotoView src={page}>
                    <img
                      src={page}
                      alt={`PDF page ${index + 1}`}
                      className="thumbnail"
                    />
                  </PhotoView>
                  <button onClick={() => deleteImage(page)} className="delete-btn">❌</button>
                </div>
              ))
            : images.map((image, index) => (
                <div key={index} className="thumbnail-wrapper">
                  <PhotoView src={image}>
                    <img
                      src={image}
                      alt={`Selected file`}
                      className="thumbnail"
                    />
                  </PhotoView>
                  <button onClick={() => deleteImage(image)} className="delete-btn">❌</button>
                </div>
              ))}
        </PhotoProvider>
      </div>
    </div>
  );
}

export default AddInvoice;