import React, { useState, useCallback } from 'react';
import { pdfjs } from 'react-pdf';
import { PhotoProvider, PhotoView } from 'react-photo-view';
import 'react-photo-view/dist/react-photo-view.css';
import axios from 'axios';
import './AddInvoice.css';

// Initialize PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function AddInvoice() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [images, setImages] = useState([]);

  const convertPdfToImages = async (file) => {
    const images = [];
    const data = await file.arrayBuffer();
    const pdf = await pdfjs.getDocument(data).promise;
    const canvas = document.createElement("canvas");
    for (let i = 0; i < pdf.numPages; i++) {
      const page = await pdf.getPage(i + 1);
      const viewport = page.getViewport({ scale: 1 });
      const context = canvas.getContext("2d");
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      await page.render({ canvasContext: context, viewport: viewport }).promise;
      images.push(canvas.toDataURL());
    }
    canvas.remove();
    return images;
  };

  const handleFileChange = useCallback(async (event) => {
    const files = Array.from(event.target.files);
    const newImages = [];
    const newFiles = [];

    for (const file of files) {
      if (file.type === 'application/pdf') {
        const pdfImages = await convertPdfToImages(file);
        newImages.push(...pdfImages);
        newFiles.push(...pdfImages.map(img => {
          const blob = dataURItoBlob(img);
          return new File([blob], `${file.name}-page-${newImages.length}.png`, { type: 'image/png' });
        }));
      } else if (file.type.startsWith('image/')) {
        newImages.push(URL.createObjectURL(file));
        newFiles.push(file);
      }
    }

    setImages(prevImages => [...prevImages, ...newImages]);
    setSelectedFiles(prevFiles => [...prevFiles, ...newFiles]);
  }, []);

  const dataURItoBlob = (dataURI) => {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) {
      alert("Please select a file to upload.");
      return;
    }

    for (const file of selectedFiles) {
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

  const deleteImage = (imageToDelete) => {
    setImages(prevImages => prevImages.filter(image => image !== imageToDelete));
    setSelectedFiles(prevFiles => prevFiles.filter((_, index) => images[index] !== imageToDelete));
  };

  return (
    <div className="add-invoice">
      <div className="drop-zone">
        <div className="icon">↑</div>
        <p>Drag and drop your files here or</p>
        <input 
          type="file" 
          accept=".jpg,.png,.pdf" 
          multiple
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
          {images.map((image, index) => (
            <div key={index} className="thumbnail-wrapper">
              <PhotoView src={image}>
                <img
                  src={image}
                  alt={`Selected file ${index + 1}`}
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