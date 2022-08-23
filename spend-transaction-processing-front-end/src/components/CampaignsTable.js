import React, { Component, useEffect } from 'react'
import { Button, TableRow, TableHead, TableBody, TableCell, TableContainer, Table, TextField, FormGroup, FormControlLabel, Switch, Paper, IconButton, Collapse, Box, CircularProgress, Alert, Typography } from "@mui/material";
import UploadService from '../services/UploadService';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';

function Row(props) {
  const { row } = props;
  const [active, setActive] = React.useState("");
  const [showSave, setShowSave] = React.useState(false);

  const handleCampaignChange = (event) => {
    // update with !row.CampaignStatus
    setActive(!active)
    // console.log(row.campaignStatus)
    // console.log(active)
  };

  useEffect(() => {
    if (active == "") {
      setActive(row.campaignStatus)
    }
  },[])

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>{row.id}</TableCell>
        <TableCell>{row.card_type}</TableCell>
        <TableCell>{row.desc}</TableCell>
        <TableCell>{row.perSpend}</TableCell>
        <TableCell>{row.reward}</TableCell>
        <TableCell>{row.rewardCurrency}</TableCell>
        <TableCell>{row.mcc}</TableCell>
        <TableCell>{row.minSpend}</TableCell>
        <TableCell>{row.endDate}</TableCell>
        <TableCell>
          <FormGroup>
              <FormControlLabel control={<Switch checked={active} onChange={handleCampaignChange} />} label={active ? "Active" : "Not Active"} />
          </FormGroup>
        </TableCell>
        {/* <TableCell>{row.pointsTransacted.toLocaleString()}</TableCell> */}
        <TableCell>
          {showSave && <Button>Save</Button>}
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}

export default function CampaignsTable() {
    const sampleJSON = {"campaigns":[{"campaign_id":5,"card_type":"SCIS Shopping Card","campaign_desc":"4 miles per dollar with Grab, min spend 100 SGD","perSpend":1,"reward":4,"rewardCurrency":"miles","minSpend":100,"isActive":1}]}
    const [campaignsToAdd, setCampaignsToAdd] = React.useState(JSON.stringify(sampleJSON));
    const [allCampaigns, setAllCampaigns] = React.useState([]);
    const [neatCampaigns, setNeatCampaigns] = React.useState([]);
    const [loading, setLoading] = React.useState(false);
    const [sendStatus, setSendStatus] = React.useState("");

    const handleChange = (e) => {
      setCampaignsToAdd(e.target.value)
      setSendStatus("")
    }

    const keyPress = (e) => {
      if (e.keyCode == 13) {
        setLoading(true);
        UploadService.addCampaign(campaignsToAdd)
        .then((response) => {
          // console.log(response.data)
          setLoading(false)
          setSendStatus("success")
        })
        .catch((e) => {
          setLoading(false)
          setSendStatus("error")
        })
      }
    }

    const sendData = (e) => {
      UploadService.addCampaign(campaignsToAdd)
        .then((response) => {
          setLoading(false)
          if (response.data.includes("Traceback")) {
            setSendStatus("error")
          } else {
            setSendStatus("success")
          }
        })
        .catch((e) => {
          setLoading(false)
          setSendStatus("error")
      })
    }

    function createData(arr) {
      return {
        id: arr[0], 
        card_type: arr[1],
        desc: arr[2], 
        perSpend: "$"+Number(arr[3]), 
        reward: arr[4] < 1.0 ? arr[4]*100+"%" : arr[4], 
        rewardCurrency: arr[5], 
        mcc: arr[6], 
        minSpend: "$"+Number(arr[7]), 
        endDate: arr[8] == "1900-01-01 00:00:00" ? "" : arr[8], 
        campaignStatus: arr[9]
      };
    }

    const handleRefresh = (e) => {
      setLoading(true);
      UploadService.getAllCampaigns()
      .then((r) => {
        setAllCampaigns(r.data.campaigns)
      })
      .then(() => {
        // console.log(allCampaigns)
        setLoading(false)
        // setSendStatus("success")
        let allNeatData = []
        allCampaigns.forEach(campaign => {
          let neatData = []
          campaign.forEach((obj, i) => {
            // console.log(campaign[i])
            for(let field in obj) {
              // console.log(obj[field])
              neatData.push(obj[field])
            }
          });
          // console.log(neatData)
          allNeatData.push(createData(neatData))
        });
        setNeatCampaigns(allNeatData)
      })
      .then(() => {
        // console.log(neatCampaigns) 
      })
      .catch((e) => {
        setLoading(false)
        // setSendStatus("error")
        // console.log(e)
      })
    }

    const wrapper = () => {
      sendData();
      handleRefresh();
    }


    return (
      <div>
        <div style={{width: "70%", display: 'flex'}}>
          <TextField
            fullWidth
            label="Campaigns"
            multiline
            rows={10}
            defaultValue={campaignsToAdd}
            onChange={handleChange}
            onKeyDown={keyPress}
          />
        </div>
          <Button onClick={wrapper}>Send</Button>
        {sendStatus != "" && 
        <Alert style={{width: "70%"}} onClose={() => {setSendStatus("")}} variant="outlined" severity={sendStatus}>
          {sendStatus == "success" && "Campaign successfully added/ updated!"}
          {sendStatus == "error" && "Please check your input"}
        </Alert>}
        <h2>
        Existing campaigns:
        <Button
          onClick={handleRefresh}
        >
          <RefreshIcon />
        </Button>
        </h2>
        <TableContainer component={Paper}>
          <Table>
          <TableHead>
            <TableRow>
              <TableCell> ID </TableCell>
              <TableCell> Card Type </TableCell>
              <TableCell> Description </TableCell>
              <TableCell> per Dollar Spend </TableCell>
              <TableCell> Reward </TableCell>
              <TableCell> Reward Currency </TableCell>
              <TableCell> MCC </TableCell>
              <TableCell> Minimum Spend </TableCell>
              <TableCell> End Date </TableCell>
              <TableCell> Campaign Status </TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
            <TableBody>
              {!loading && neatCampaigns.map((row) => (
                <Row key={row.id} row={row} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {loading && 
        <Box sx={{ display: 'flex' }} style={{width:"100%", justifyContent: 'center'}}>
          <CircularProgress />
        </Box>
        }
      </div>
    )
}
