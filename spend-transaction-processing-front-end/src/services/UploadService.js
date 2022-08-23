import http from './httpCommon';
import axios from 'axios';
class UploadService {
  uploadUsers(file) {
    let formData = new FormData();

    formData.append('user_file', file)

    return http.post('/user/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
  
  uploadTransaction(file) {
    let formData = new FormData();

    formData.append('transaction_file', file)

    return http.post('/transaction/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  getRewardsByUserId(req) {
    return axios.post('https://server.itsag1t4.com/transaction/rewardpoint', req)
  }

  getAllCampaigns() {
    return axios.get('https://server.itsag1t4.com/campaign/view_campaigns')
  }

  addCampaign(campaigns) {
    return axios.post('https://server.itsag1t4.com/campaigns/add_campaigns', campaigns)
  }
}

export default new UploadService();
