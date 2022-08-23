import React from "react";
import { render } from "react-dom";
import { Button, TableRow, TableHead, TableBody, TableCell, Table, TextField, FormGroup, FormControlLabel, Switch } from "@mui/material";

class TableDemo extends React.Component {
  state = {
    rows: [{}]
  };
  handleChange = idx => e => {
    const { name, value } = e.target;
    const rows = [...this.state.rows];
    rows[idx] = {
      [name]: value
    };
    this.setState({
      rows
    });
  };
  handleAddRow = () => {
    const item = {
      name: "",
      mobile: ""
    };
    this.setState({
      rows: [...this.state.rows, item]
    });
  };
  handleRemoveRow = () => {
    this.setState({
      rows: this.state.rows.slice(0, -1)
    });
  };
  handleRemoveSpecificRow = (idx) => () => {
    const rows = [...this.state.rows]
    rows.splice(idx, 1)
    this.setState({ rows })
  }
  render() {
    return (
      <div>
        <div className="container">
          <div className="row clearfix">
            <div className="col-md-12 column">
              <Table
                className="table table-bordered table-hover"
                id="tab_logic"
              >
                <TableHead>
                  <TableRow>
                    <TableCell className="text-center"> # </TableCell>
                    <TableCell className="text-center"> Name </TableCell>
                    <TableCell className="text-center"> Mobile </TableCell>
                    <TableCell />
                  </TableRow>
                </TableHead>
                <TableBody>
                  {this.state.rows.map((item, idx) => (
                    <TableRow id="addr0" key={idx}>
                      <TableCell>{idx+1}</TableCell>
                      <TableCell>
                        <TextField
                          label="name"
                          value={this.state.rows[idx].name}
                          onChange={this.handleChange(idx)}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          label="mobile"
                          value={this.state.rows[idx].mobile}
                          onChange={this.handleChange(idx)}
                        />
                      </TableCell>
                      <TableCell>
                        {/* <Button
                          className="btn btn-outline-danger btn-sm"
                          onClick={this.handleRemoveSpecificRow(idx)}
                        >
                          Remove
                        </Button> */}
                        <FormGroup>
                            <FormControlLabel control={<Switch defaultChecked />} label={true ? "ON" : "OFF"} />
                        </FormGroup>
                        <Button
                          className="btn btn-outline-danger btn-sm"
                          onClick={this.handleRemoveSpecificRow(idx)}
                        >
                          Save
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <Button onClick={this.handleAddRow} className="btn btn-primary">
                Add Row
              </Button>
              <Button
                onClick={this.handleRemoveRow}
                className="btn btn-danger float-right"
              >
                Delete Last Row
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

render(<TableDemo />, document.getElementById("root"));
export default TableDemo;