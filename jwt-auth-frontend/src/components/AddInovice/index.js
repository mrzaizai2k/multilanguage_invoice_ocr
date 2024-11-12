import React, { useState, useCallback } from 'react';
import { pdfjs } from 'react-pdf';
import { PhotoProvider, PhotoView } from 'react-photo-view';
import 'react-photo-view/dist/react-photo-view.css';
import { notification, Spin, Progress } from 'antd';
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
  const [fileNames, setFileNames] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [loadingAddFile, setLoadingAddFile] = useState(false);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

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
      const viewport = page.getViewport({ scale: 2 });
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
    let fileNamesToAdd = [];

    for (const file of newFiles) {
      if (file.size > MAX_FILE_SIZE) {
        notification.warning({
          message: 'File Size Exceeded',
          description: `File "${file.name}" exceeds the maximum limit of 5MB.`,
        });
        continue;
      }

      if (file.type === 'application/pdf') {
        const pdfImages = await convertPdfToImages(file);
        for (let i = 0; i < pdfImages.length; i++) {
          const blob = dataURItoBlob(pdfImages[i]);
          if (blob.size > MAX_FILE_SIZE) {
            notification.warning({
              message: 'Extracted Image Size Exceeded',
              description: `Extracted image from PDF (page ${i + 1}) exceeds the maximum limit of 5MB.`,
            });
            continue;
          }
          imagesToAdd.push(pdfImages[i]);
          filesToAdd.push(new File([blob], `${file.name}-page-${i + 1}.png`, { type: 'image/png' }));
          fileNamesToAdd.push(file.name); // Store original PDF name for each extracted image
        }
      } else if (file.type.startsWith('image/')) {
        imagesToAdd.push(URL.createObjectURL(file));
        filesToAdd.push(file);
        fileNamesToAdd.push(file.name); // Store original image name
      }
    }

    if (filesToAdd.length > 0) {
      setImages(prevImages => [...prevImages, ...imagesToAdd]);
      setSelectedFiles(prevFiles => [...prevFiles, ...filesToAdd]);
      setFileNames(prevNames => [...prevNames, ...fileNamesToAdd]);
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
        description: 'Please select files to upload.',
      });
      return;
    }
  
    const MAX_BATCH_SIZE = 10;
    const RETRY_LIMIT = 3;
    let currentBatchIndex = 0;
    
    notification.warning({
      message: 'Upload in Progress',
      description: 'Please do not close this tab until the upload is complete.',
      duration: 0,
    });
  
    setLoadingUpload(true);
    setUploadProgress(0);
  
    const uploadSingleFile = async (file, fileName, retryCount = 0) => {
      try {
        const base64Image = await imageToBase64(file);
        const payload = {
          img: base64Image,
          user_uuid: username,
          file_name: fileName
        };
        await createInvoice(payload);
        return { success: true };
      } catch (error) {
        if (error?.response?.status === 429 && retryCount < RETRY_LIMIT) {
          // Wait 60 seconds before retrying if we hit rate limit
          await new Promise(resolve => setTimeout(resolve, 60000));
          return uploadSingleFile(file, fileName, retryCount + 1);
        }
        return { success: false, error };
      }
    };

    const uploadBatch = async (batchFiles, batchFileNames) => {
      const results = await Promise.all(
        batchFiles.map((file, idx) => 
          uploadSingleFile(file, batchFileNames[idx])
        )
      );

      // Check if any uploads failed due to rate limiting
      const failedUploads = results.map((result, idx) => ({
        file: batchFiles[idx],
        fileName: batchFileNames[idx],
        success: result.success,
        error: result.error
      })).filter(item => !item.success);

      if (failedUploads.length > 0) {
        // Wait 60 seconds before retrying failed uploads
        await new Promise(resolve => setTimeout(resolve, 60000));
        
        // Retry failed uploads
        const retryResults = await Promise.all(
          failedUploads.map(item => 
            uploadSingleFile(item.file, item.fileName)
          )
        );

        // If any retries still failed, throw error
        const stillFailed = retryResults.some(result => !result.success);
        if (stillFailed) {
          throw new Error('Upload failed after retries');
        }
      }
    };
  
    try {
      while (currentBatchIndex < selectedFiles.length) {
        const batchFiles = selectedFiles.slice(
          currentBatchIndex,
          currentBatchIndex + MAX_BATCH_SIZE
        );
        const batchFileNames = fileNames.slice(
          currentBatchIndex,
          currentBatchIndex + MAX_BATCH_SIZE
        );
  
        await uploadBatch(batchFiles, batchFileNames);
        
        // Update progress
        const progress = Math.min(
          Math.round((currentBatchIndex + MAX_BATCH_SIZE) / selectedFiles.length * 100),
          100
        );
        setUploadProgress(progress);
  
        currentBatchIndex += MAX_BATCH_SIZE;

        // Add 0.5-second delay between each batch
        await new Promise(resolve => setTimeout(resolve, 500));
      }
  
      notification.destroy();
      
      notification.success({
        message: 'Upload Complete',
        description: 'All files uploaded successfully!',
      });
  
      setSelectedFiles([]);
      setImages([]);
      setFileNames([]);
      setUploadProgress(0);
    } catch (error) {
      notification.destroy();
      
      notification.error({
        message: 'Upload Failed',
        description: 'Error uploading files: ' + error,
      });
    } finally {
      setLoadingUpload(false);
    }
  };


  const deleteImage = (imageToDelete) => {
    const indexToDelete = images.indexOf(imageToDelete);
    setImages(prevImages => prevImages.filter(image => image !== imageToDelete));
    setSelectedFiles(prevFiles => prevFiles.filter((_, index) => index !== indexToDelete));
    setFileNames(prevNames => prevNames.filter((_, index) => index !== indexToDelete));
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
          <div className="upload-section">
            {loadingUpload && (
              <div className="upload-progress">
                <Progress percent={uploadProgress} status="active" />
              </div>
            )}
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
          </div>
        )}
      </div>
    </>
  );
}

export default AddInvoice;