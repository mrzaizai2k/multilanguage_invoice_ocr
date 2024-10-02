/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useCallback, useRef } from 'react';
import { pdfjs } from 'react-pdf';
import { PhotoProvider, PhotoView } from 'react-photo-view';
import 'react-photo-view/dist/react-photo-view.css';
import { notification, Spin } from 'antd';
import { BsFiletypeJpg, BsFiletypePdf, BsFiletypePng, BsTrash3Fill, BsUpload } from "react-icons/bs";
import { MdAddToPhotos, MdOutlineZoomOutMap } from "react-icons/md";
import { Helmet } from 'react-helmet';
import { createInvoice } from '../../services/api';
import './AddInvoice.css';

// Initialize PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function AddInvoice({ username }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [images, setImages] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [loadingAddFile, setLoadingAddFile] = useState(false);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  const totalSizeRef = useRef(0);

  const imageToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = error => reject(error);
    });
  };

  const convertPdfToImages = async (file) => {
    const images = [];
    const data = await file.arrayBuffer();
    const pdf = await pdfjs.getDocument(data).promise;
    const canvas = document.createElement('canvas');

    for (let i = 0; i < pdf.numPages; i++) {
      const page = await pdf.getPage(i + 1);
      const viewport = page.getViewport({ scale: 1 });
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      await page.render({ canvasContext: context, viewport }).promise;
      images.push(canvas.toDataURL());
    }
    canvas.remove();
    return images;
  };

  const handleFileChange = useCallback(async (newFiles) => {
    setLoadingAddFile(true);
    let filesToAdd = [];
    let imagesToAdd = [];

    for (const file of newFiles) {
      if (file.size > MAX_FILE_SIZE) {
        notification.warning({
          message: 'File Size Exceeded',
          description: `File "${file.name}" exceeds the maximum limit of 5MB.`,
        });
        continue;
      }

      if (totalSizeRef.current + file.size > MAX_FILE_SIZE) {
        notification.warning({
          message: 'Total File Size Exceeded',
          description: 'The total size of all files would exceed the 5MB limit.',
        });
        break;
      }

      totalSizeRef.current += file.size;

      if (file.type === 'application/pdf') {
        const pdfImages = await convertPdfToImages(file);
        imagesToAdd.push(...pdfImages);
        filesToAdd.push(...pdfImages.map(img => {
          const blob = dataURItoBlob(img);
          return new File([blob], `${file.name}-page-${imagesToAdd.length}.png`, { type: 'image/png' });
        }));
      } else if (file.type.startsWith('image/')) {
        imagesToAdd.push(URL.createObjectURL(file));
        filesToAdd.push(file);
      }
    }

    if (filesToAdd.length > 0) {
      setImages(prevImages => [...prevImages, ...imagesToAdd]);
      setSelectedFiles(prevFiles => [...prevFiles, ...filesToAdd]);
    }

    setLoadingAddFile(false);
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
      notification.warning({
        message: 'No Files Selected',
        description: 'Please select a file to upload.',
      });
      return;
    }

    setLoadingUpload(true);
    try {
      for (const file of selectedFiles) {
        const base64Image = await imageToBase64(file);
        const payload = {
          img: base64Image,
          user_uuid: username
        };
        await createInvoice(payload);
      }

      notification.success({
        message: 'Upload Successful',
        description: 'All files uploaded successfully!',
      });
      setSelectedFiles([]);
      setImages([]);
      totalSizeRef.current = 0;
    } catch (error) {
      notification.error({
        message: 'Upload Failed',
        description: 'Error uploading file: ' + error,
      });
    } finally {
      setLoadingUpload(false);
    }
  };

  const deleteImage = (imageToDelete) => {
    setImages(prevImages => prevImages.filter(image => image !== imageToDelete));
    setSelectedFiles(prevFiles => prevFiles.filter((_, index) => images[index] !== imageToDelete));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    await handleFileChange(files);
  };

  return (
    <>
      <Helmet>
        <title>Add Invoice</title>
      </Helmet>
      <div className="add-invoice">
        <div className={`drop-zone ${dragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {loadingAddFile ? (
            <div className="loading-spinner">
              <Spin size="large" />
            </div>
          ) : images.length > 0 ? (
            <PhotoProvider toolbarRender={({ rotate, onRotate }) => {
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
            }}>
              <div className="thumbnail__list">
                {images.map((image, index) => (
                  <div className="thumbnail__item" key={index}>
                    <img src={image} alt={`Selected file ${index + 1}`} />
                    <div className="thumbnail__item-overlay">
                      <PhotoView src={image}>
                        <button className="zoom-btn">
                          <MdOutlineZoomOutMap />
                        </button>
                      </PhotoView>
                      <button className="delete-btn" onClick={() => deleteImage(image)}>
                        <BsTrash3Fill />
                      </button>
                    </div>
                  </div>
                ))}
                <div className="thumbnail__item-addmore">
                  <input id='file2' type="file" accept=".jpg,.png,.pdf" multiple onChange={(e) => handleFileChange(Array.from(e.target.files))} hidden />
                  <label htmlFor='file2' className="add-more-file">
                    <h3>Add more files</h3>
                    <MdAddToPhotos />
                  </label>
                </div>
              </div>
            </PhotoProvider>
          ) : (
            <>
              <div className="icon-upload"><BsUpload /></div>
              <p>Drag and drop your image here</p>
              <span className='or'>or</span>
              <label htmlFor='file' className="browse-btn">Browse File</label> <br/>
              <span style={{display: "block", paddingTop: "15px", color: "red"}}>Upload max file size 5MB</span>
              <input id='file' type="file" accept=".jpg,.png,.pdf" multiple onChange={(e) => handleFileChange(Array.from(e.target.files))} hidden />
              <div className="file-types">
                <BsFiletypeJpg />
                <BsFiletypePng />
                <BsFiletypePdf />
              </div>
            </>
          )}
        </div>
        {images.length > 0 && (
          <button className="upload-btn" onClick={handleUpload} disabled={loadingUpload}>
            {loadingUpload ? (
              <>
                <Spin size="small" />
                <span style={{ marginLeft: '8px' }}>Uploading...</span>
              </>
            ) : (
              <>
                <BsUpload style={{ fontSize: "20px", marginRight: '8px' }} />
                <span>Upload</span>
              </>
            )}
          </button>
        )}
        {images.length > 0 && (
          <div style={{marginTop: "10px"}}>
            <p>Total size: {(totalSizeRef.current / (1024 * 1024)).toFixed(2)} MB / 5 MB</p>
          </div>
        )}  
      </div>
    </>
  );
}

export default AddInvoice;
