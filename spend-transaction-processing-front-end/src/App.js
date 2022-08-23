import React, {useState, useEffect, useRef} from 'react'
import ResponsiveAppBar from './components/ResponsiveAppBar';
import ClientTransactionsTable from './components/ClientTransactionsTable';
import UploadUsers from './components/UploadUsers';
import UploadTransactions from './components/UploadTransactions';
import { Button, Alert, Card, Typography } from '@mui/material';
import UploadService from './services/UploadService';
import CampaignsTable from './components/CampaignsTable'

function SpendTransactionProcessing() {
	const [menuSelected, setMenuSelected] = React.useState('Client Transactions');
	const uploadUsersRef = useRef();
	const uploadTransactionsRef = useRef();

	return (
		<div>
			<ResponsiveAppBar menuSelected={menuSelected} setMenuSelected={setMenuSelected} />
			{menuSelected == "Client Transactions" && <ClientTransactionsTable />}
			{menuSelected == "Campaigns Management" && 
				<>
					<br/>
					<CampaignsTable />
				</>
			}
			{menuSelected == "Upload" && 
				<>
				<br />
				<Card>
					<Typography variant="h6" style={{margin: "1%"}}>
						You may upload one file at a time for users, one file at a time for transactions. You may click upload with only the user file, or only the transaction file, or with both files together.
					</Typography>
				</Card>
				<br />
				<div style={{display:'flex', justifyContent: 'space-evenly'}}>
					<UploadUsers ref={uploadUsersRef} />
					<UploadTransactions ref={uploadTransactionsRef}/>
				</div>
				<div style={{display: 'flex', width: "100%", justifyContent: 'center'}}>
					<Button
					className="btn btn-success"
					variant='contained'
					style={{}}
					onClick={() => {
						uploadUsersRef.current.uploadUser();
						uploadTransactionsRef.current.uploadTxn();
					}}
					>
					Upload
					</Button>
				</div>
				</>
			}
		</div>
	)
}

export default SpendTransactionProcessing