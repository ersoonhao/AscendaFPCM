import React, { Component } from 'react';
import Dropzone from 'react-dropzone';
import UploadService from '../services/UploadService';
import { Box, Button, Typography } from '@mui/material';

export default class UploadUsers extends Component {
  constructor(props) {
    super(props);
    this.uploadUser = this.uploadUser.bind(this);
    this.onDrop = this.onDrop.bind(this);

    this.state = {
      selectedFiles: undefined,
      currentFile: undefined,
      progress: 0,
      loading: false,
      message: '',
      fileInfos: [],
    };
  }

  componentDidMount() {
    UploadService.uploadUsers().then((response) => {
      this.setState({
        fileInfos: response.data,
      });
    });
  }

  uploadUser() {
    try {
      let currentFile = this.state.selectedFiles[0];
      this.setState({
        // progress: 0,
        loading: false,
        message: "",
        currentFile: currentFile,
      });
      UploadService.uploadUsers(currentFile, (event) => {
        this.setState({
          // progress: Math.round((100 * event.loaded) / event.total),
          loading: true,
          message: "Loading..."
        });
      })
      .then((response) => {
        if (response.data.includes("Traceback")) {
          throw "";
        }
        this.setState({
          message: response.data,
          loading: false,
        });
        return UploadService.uploadUsers();
        })
        .catch(() => {
          this.setState({
            // progress: 0,
            message: 'Could not upload the user file!',
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
            <section>
            <Typography variant="h4"> Upload User </Typography>
            <div {...getRootProps({ className: 'dropzone' })} style={{border: "3px dashed #eeeeee", height: "40vh", width: "30vw", backgroundColor: '#fafafa', color: '#bdbdbd', cursor: 'pointer', marginBottom: 20, marginTop: 20}}>
                <input {...getInputProps()} />
                {selectedFiles && selectedFiles[0].name ? (
                <div className="selected-file">
                    {selectedFiles && selectedFiles[0].name}
                </div>
                ) : (
                    <div style={{display: "flex", alignItems: "center", height: 'inherit', justifyContent: 'center'}}>
                        Drag and drop user file here, or click to select file
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
            </section>
        )}
        </Dropzone>

        <div className="alert alert-light" role="alert">
          {message}
        </div>

        {/* {fileInfos.length > 0 && (
          <div className="card">
            <div className="card-header">List of Files</div>
            <ul className="list-group list-group-flush">
              {fileInfos.map((file, index) => (
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
