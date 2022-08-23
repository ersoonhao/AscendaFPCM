import * as React from 'react';
import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';
import IconButton from '@mui/material/IconButton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { Alert, TextField } from '@mui/material';
import UploadService from '../services/UploadService';
import Chip from '@mui/material/Chip';
import Stack from '@mui/material/Stack';
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
// 07661502-f08a-4391-a274-d8d8b9bdfc54
// b044eeea-5818-461b-a005-372b0ee53647

function createData(date, transactionSummary, type, pointsTransacted, remarks, amountSpent, spendCurrency, score_unit) {
  return {
    date,
    transactionSummary,
    type,
    pointsTransacted,
    details: 
      {
        remarks: remarks,
        amountSpent: amountSpent,
        spendCurrency: spendCurrency
      }
    ,
    score_unit
  };
}

function Row(props) {
  const { row } = props;
  const [open, setOpen] = React.useState(false);

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell component="th" scope="row">
          {row.date}
        </TableCell>
        <TableCell align="right">{row.transactionSummary}</TableCell>
        <TableCell align="right">
        <Chip label={row.type} color="primary" variant="outlined" />
          {/* {row.type} */}
        </TableCell>
        <TableCell align="right">{row.pointsTransacted.toLocaleString()} {row.score_unit}</TableCell>
        <TableCell align="right" style={{color: '#3e3e3e'}}>
            {open ? "Hide Details" : "View Details"}
            <IconButton
                aria-label="expand row"
                size="small"
                onClick={() => setOpen(!open)}
            >
                {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
            </IconButton>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
                <b>Remarks</b>: {row.details.remarks}
                <br/>
                <b>Amount Spent</b>: {row.details.spendCurrency}${row.details.amountSpent.toLocaleString()}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}

Row.propTypes = {
  row: PropTypes.shape({
    date: PropTypes.string.isRequired,
    transactionSummary: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    pointsTransacted: PropTypes.number.isRequired,
    details: PropTypes.shape(
      {
        remarks: PropTypes.string.isRequired,
        amountSpent: PropTypes.number || PropTypes.string,
      },
    ).isRequired,
    name: PropTypes.string,
  }).isRequired,
};

export default function ClientTransactionsTable() {
  const [userId, setUserId] = React.useState("");
  const [msg, setMsg] = React.useState("Please enter the customer ID to retrieve their transaction summary.");
  const [rows, setRows] = React.useState([]);
  const [shortRows, setShortRows] = React.useState([]);
  const [pageNo, setPageNo] = React.useState(1);
  const PAGE_SIZE = 3;
  const [showRightPagination, setShowRightPagination] = React.useState(false);
  const [isInitialCall, setIsInitialCall] = React.useState(true);
  const [sendStatus, setSendStatus] = React.useState("");

  const handleChange = (e) => {
    setUserId(e.target.value);
    setSendStatus("")
  }

  const keyPress = (e) => {
    if (e.keyCode == 13) {
      setUserId(e.target.value);
      UploadService.getRewardsByUserId({
        "user_id": userId,
        "page_size": PAGE_SIZE*2,
        "page_number": 1,
      })
      .then((response) => {
        setMsg("")
        setPageNo(1)
        let res = response.data
        let temp = []
        if (res.length > 0) {
          res.forEach(arr => {
            temp.push(createData(arr.transaction_date, arr.transaction_summary, 'Earn', arr.card_score, arr.card_campaign,  arr.transaction_spent, arr.transaction_currency, arr.score_unit))
          });
        setRows(temp)
        setShortRows(temp.slice(0,PAGE_SIZE))
        setShowRightPagination(true)
        setSendStatus("success")
        } else {
          setRows([])
          setSendStatus("error")
          setMsg("No transactions found")
        }
        if (response.data.includes("Traceback")) {
          setSendStatus("error")
        } 
      })
      .catch((e) => {
        setSendStatus("error")
        // console.log(e)
        // setMsg("Failed to retrieve user")
      })
    }
  }

  const nextPage = () => {
    if (msg.includes("no")) {
      return
    }
    setMsg("")
    setSendStatus("")
    setPageNo(pageNo+1)
    UploadService.getRewardsByUserId({
      "user_id": userId,
      "page_size": PAGE_SIZE,
      "page_number": pageNo+1+(isInitialCall ? 1 : 0),
    })
    .then((response) => {
      let res = response.data
      // console.log(rows)
      // console.log(((pageNo+1)*PAGE_SIZE-PAGE_SIZE),((pageNo+1)*PAGE_SIZE))
      if (res.length > 0) {
        let temp2 = []
        res.forEach(arr => {
          temp2.push(createData(arr.transaction_date, arr.transaction_summary, 'Earn', arr.card_score, arr.card_campaign,  arr.transaction_spent, arr.transaction_currency, arr.score_unit))
        });
        let temp3 = rows
        setRows(temp3.concat(temp2))
        setShortRows(temp3.slice(((pageNo+1)*PAGE_SIZE-PAGE_SIZE),((pageNo+1)*PAGE_SIZE)))
      } else {
        setShortRows(rows.slice(((pageNo+1)*PAGE_SIZE-PAGE_SIZE),((pageNo+1)*PAGE_SIZE)))
        // setMsg("no other transactions found")
        setShowRightPagination(false)
      }
    })
  }

  const previousPage = () => {
    setMsg("")
    setSendStatus("")
    setPageNo(pageNo-1)
    setShortRows(rows.slice(((pageNo-1)*PAGE_SIZE-PAGE_SIZE),((pageNo-1)*PAGE_SIZE)))
    setShowRightPagination(true)
  }

  return (
    <>
    <TextField
      label="Customer ID"
      value={userId}
      onChange={handleChange}
      onKeyDown={keyPress}
      style={{marginTop: 20}}
    />
    {sendStatus != "" && 
    <Alert style={{width: "50%"}} onClose={() => {setSendStatus("")}} variant="outlined" severity={sendStatus}>
      {sendStatus == "success" && "Successfully retrieved all customer transactions!"}
      {sendStatus == "error" && "No transactions found, please enter a new customer ID!"}
    </Alert>}
    {<TableContainer component={Paper}>
      <Table aria-label="collapsible table">
        <TableHead>
          <TableRow>
            <TableCell><b>Date</b></TableCell>
            <TableCell align="right"><b>Transaction Summary</b></TableCell>
            <TableCell align="right"><b>Type</b></TableCell>
            <TableCell align="right"><b>Rewards Transacted</b></TableCell>
          </TableRow>
        </TableHead>
        {(shortRows.length > 0) && 
        <TableBody>
          {shortRows.map((row,i) => (
            <Row key={i} row={row} />
          ))}
        </TableBody>}
      </Table>
    </TableContainer>}
    {
    <div style={{width:"100%", justifyContent: 'center', display: 'flex', placeItems: 'center'}}>
      {<IconButton disabled={pageNo < 2} onClick={previousPage}>
        <ArrowBackIosNewIcon/>
      </IconButton>
      }
      {shortRows.length> 0 && 
      <Typography variant="h6">
      {pageNo}
      </Typography>}
      {<IconButton disabled={!showRightPagination} onClick={nextPage}>
        <ArrowForwardIosIcon/>
      </IconButton>}
    </div>}
    <div><br/>
    
    {/* {msg} */}
    </div>
    </>
  );
}
