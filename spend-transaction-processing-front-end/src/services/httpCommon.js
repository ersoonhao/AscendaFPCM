import axios from 'axios';

export default axios.create({
  baseURL: 'https://server.itsag1t4.com',
  headers: {
    'Content-type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  },
});
 