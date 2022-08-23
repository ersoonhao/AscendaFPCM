import React, { Component } from 'react';
import Dropzone from 'react-dropzone';
import UploadService from '../services/UploadService';
import { Box, Button, Typography } from '@mui/material';

export default class UploadTransactions extends Component {
  constructor(props) {
    super(props);
    this.uploadTxn = this.uploadTxn.bind(this);
    this.onDrop = this.onDrop.bind(this);

    this.state = {
      selectedFiles: undefined,
      currentFile: undefined,
      // progress: 0,
      message: '',
      fileInfos: [],
    };
  }

  componentDidMount() {
    UploadService.uploadTransaction().then((response) => {
      this.setState({
        fileInfos: [response.data],
      });
    });
  }

  uploadTxn() {
    try {
      let currentFile = this.state.selectedFiles[0];
      this.setState({
        // progress: 0,
        currentFile: currentFile,
      });

      UploadService.uploadTransaction(currentFile, (event) => {
        this.setState({
          message: "",
          // progress: Math.round((100 * event.loaded) / event.total),
        });
      })
        .then((response) => {
          // console.log(response.data)
          if (response.data.includes("Traceback")) {
            throw "";
          }
          this.setState({
            message: response.data,
          });
          return UploadService.uploadTransaction();
        })
        .catch(() => {
          this.setState({
            // progress: 0,
            message: 'Could not upload the transaction file!',
            currentFile: undefined,
          });
        });
  
      this.setState({
        selectedFiles: undefined,
      });
    } catch (error) {
      // console.log(error)
      return
    }

  }

  onDrop(files) {
    if (files.length > 0) {
      this.setState({ 
        selectedFiles: files,
        message: "",
      });
    }
  }

  render() {
    const { selectedFiles, currentFile, progress, message, fileInfos } =
      this.state;

    return (
      <div>
        {/* {currentFile && (
          <div className="progress mb-3">
            <div
              className="progress-bar progress-bar-info progress-bar-striped"
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin="0"
              aria-valuemax="100"
              style={{ width: progress + '%' }}
            >
              {progress}%
            </div>
          </div>
        )} */}
        
        <Dropzone onDrop={this.onDrop} multiple={false}>
        {({ getRootProps, getInputProps }) => (
            <Box>
            <Typography variant="h4"> Upload Transactions </Typography>
            <div {...getRootProps({ className: 'dropzone' })} style={{border: "3px dashed #eeeeee", height: "40vh", width: "30vw", backgroundColor: '#fafafa', color: '#bdbdbd', cursor: 'pointer', marginBottom: 20, marginTop: 20}}>
                <input {...getInputProps()} />
                {selectedFiles && selectedFiles[0].name ? (
                <div className="selected-file">
                    {selectedFiles && selectedFiles[0].name}
                </div>
                ) : (
                    <div style={{display: "flex", alignItems: "center", height: 'inherit', justifyContent: 'center'}}>
                        Drag and drop transaction file here, or click to select file
                    </div>
                )}
            </div>
            {/* <div style={{display: 'flex', width: "30vw", justifyContent: 'center'}}>
                <Button
                className="btn btn-success"
                variant='contained'
                disabled={!selectedFiles}
                onClick={this.upload}
                >
                Upload
                </Button>
            </div> */}
            </Box>
        )}
        </Dropzone>

        <div className="alert alert-light" role="alert">
          {message}
        </div>

        {/* {fileInfos.length > 0 && (
          <div className="card">
            <div className="card-header">List of Files</div>
            <ul className="list-group list-group-flush">
              {fileInfos((file, index) => (
                <li className="list-group-item" key={index}>
                  <a href={file.url}>{file.name}</a>
                </li>
              ))}
            </ul>
          </div>
        )} */}
      </div>
    );
  }
}
