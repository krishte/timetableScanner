import './App.css';
import React, { useState, useEffect } from 'react';
import TimetableEdit from './TimetableEdit';
import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image';
import Spinner from 'react-bootstrap/Spinner';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import InputGroup from 'react-bootstrap/InputGroup';



function App() {
 
  const [timetableImg, setTimetableImg] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [croppedPos, setCroppedPos] = useState(null);
  // const [summaries, setSummaries] = useState(null);
  // const [times, setTimes]  = useState(null);
  // const [days, setDays]  = useState(null);
  // const [weeks, setWeeks] = useState(null);
  const [events, setEvents] = useState(null);
  const [croppedURLs, setCroppedURLs] = useState(null)
  const [loading, setLoading] = useState(false)
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [horizontalLines, setHorizontalLines] = useState(null)
  const [timeBoxes, setTimeBoxes] = useState(null);
  const [timeCroppedURLs, setTimeCroppedURLs] = useState(null);
  

  const handleStartDateChange = (event) => {
    setStartDate(event.target.value);
  }

  const handleEndDateChange = (event) => {
    setEndDate(event.target.value)
  }

  const handleFileChange = (event) => {
    setUploadedFile(event.target.files[0]);
  };

  const cropImage = async (src, x, y, width, height) => {
    return new Promise((resolve, reject) => {
      const image = document.createElement('img');
      image.src = src;
      image.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;
        //console.log(x, y, width, height);
        ctx.drawImage(image, x, y, width, height, 0, 0, width, height);
        const croppedDataUrl = canvas.toDataURL('image/jpeg');
        resolve(croppedDataUrl);
      };
      image.onerror = reject;
    });
  }

  const cropImages = async (passedCroppedPos, resizedImageURL, passedTimeBoxes, passedHorizontalLines) => {
    Promise.all(
      passedCroppedPos.map((item) => cropImage(resizedImageURL, item[0], item[1], item[2]-item[0], item[3]-item[1]))
    )
    .then((croppedDataUrls) => {
      setCroppedURLs(croppedDataUrls)
      Promise.all(
        passedTimeBoxes.map((item) => cropImage(resizedImageURL, item[1], passedHorizontalLines[item[2]], item[3]-item[1], passedHorizontalLines[item[4]]-passedHorizontalLines[item[2]]))
      )
      .then((croppedTimeDataUrls) => {
        setTimeCroppedURLs(croppedTimeDataUrls)
        setTimetableImg(true);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    })
    .catch((error) => {
      console.error('Error:', error);
    });


    
    
  }

  const getResizedImage = async (croppedPosNew, croppedWidth, timeBoxesNew, horizontalLinesNew) => {
    const formData = new FormData();
    formData.append("timetableFile",uploadedFile);
    formData.append("croppedWidth", croppedWidth)
    console.log("POSTing 2")
    fetch('http://172.20.135.41:5001/resizeImage', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.blob()
    })
    .then(blob => {
        setUploadedFile(blob)
        cropImages(croppedPosNew, URL.createObjectURL(blob), timeBoxesNew, horizontalLinesNew)

    }).catch(err => {
      console.log(err);
    })  
  }
  
  const handleFileUpload = async () => {
    const formData = new FormData();
    if (isNaN(new Date(startDate))) {
      alert("Start date is invalid.")
      return;
    }
    else if (isNaN(new Date(endDate))) {
      alert("End date is invalid")
      return;
    }
    else if (new Date(endDate) <= new Date(startDate)) {
      alert("Start date must occur before End date")
      return;
    }
    setLoading(true);

    formData.append("timetableFile",uploadedFile);
    console.log("POSTing")
    fetch('http://172.20.135.41:5001/processTimetable', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json()
    })
    .then(data => {
      //console.log(data)
      if (!data.success) {
        setLoading(false);
        alert(data.error)
        
      }
      else {
        setCroppedPos(data.cropped_pos)
        // setSummaries(data.summaries)
        // setTimes(data.times)
        // setDays(data.days)
        // setWeeks(data.weeks)
        setEvents(data.events)
        console.log(data.events)
        setTimeBoxes(data.timeBoxes)
        setHorizontalLines(data.horizontalLines)
        getResizedImage(data.cropped_pos, data.croppedWidth, data.timeBoxes, data.horizontalLines)
      }
    }).catch(err => {
      console.log(err);
      setLoading(false);
      alert("there was an issue connecting to the server. Please try again later.")
     
    })
    
  }

  let uploadPreview;
  if (uploadedFile) {
    uploadPreview = (
      <Form.Group  style={{padding: "30px", position:"relative", textAlign:"center"}}>
        <Image src={URL.createObjectURL(uploadedFile)} style={{opacity:(loading ? 0.5:1.0) }}fluid/>
        {loading &&
        <div className='centered'>
          <Spinner animation="border" variant="primary" />
        </div>
        }
      </Form.Group>
    );
  }

  let buttontext;
  if (loading)
  {
    buttontext = (
    <Button variant="primary" style={{width:"100%"}}>
      <Spinner
        as="span"
        animation="grow"
        size="sm"
        role="status"
        aria-hidden="true"
      />
      Loading..
    </Button>);
  }
  else if (!uploadedFile) {
    buttontext = (<Button variant="secondary" onClick={handleFileUpload} style={{width:"100%"}} disabled>
      Upload File
    </Button>);
  }
  else {
    buttontext = (<Button variant="primary" onClick={handleFileUpload} style={{width:"100%"}}>
    Upload File
  </Button>);
  }

  let currentView;
  if (timetableImg) {
    currentView = (
      <TimetableEdit
        backgroundImg={uploadedFile}
        croppedPos={croppedPos}
        events={events}
        // summaries={summaries}
        // times={times}
        // days={days}
        // weeks={weeks}  
        croppedURLs={croppedURLs}
        startDate={startDate}
        endDate={endDate}
        timeCroppedURLs={timeCroppedURLs}
        horizontalLines={horizontalLines}
        timeBoxes={timeBoxes}
      />
    )
  }
  else {
    currentView = (
      <div>
        <h1>Timetable to ICS</h1>
        <Col xs={12} sm={12} md={8} lg={6} xl={6}>
        <p >This free online timetable scanner allows you to transfer information directly from a timetable to your preferred calendar service via an ics file. Upload a PNG of JPEG to get started.</p>
        </Col>
        <div className='border-secondary border rounded-3 shadow bg-secondary-subtle'>
        <Form.Group  style={{padding: "30px"}}>
          <Form.Control type="file" accept="image/*" onChange={handleFileChange} />
        </Form.Group>
        <Form.Group style={{padding: "30px"}}>
          <Row>
            <Col>
              <InputGroup className="mb-3">
                <InputGroup.Text id="basic-addon1">Start date</InputGroup.Text>
                <Form.Control
                  type="date"
                  className="startDate"
                  value={startDate}
                  onChange={handleStartDateChange}
                />  
              </InputGroup>   
            </Col>
            <Col>
              <InputGroup className="mb-3">
                <InputGroup.Text id="basic-addon1">End date</InputGroup.Text>
                <Form.Control
                  type="date"
                  className="endDate"
                  value={endDate}
                  onChange={handleEndDateChange}
                />  
              </InputGroup> 
            </Col>
          </Row>
          </Form.Group>
          </div>
          {uploadPreview}
        <Form.Group style={{padding: "30px"}}>
          {buttontext}
        </Form.Group>
      </div>
    );
  }


  return (

    <Container fluid="md" style={{padding:"30px"}}>
      {currentView}
    </Container>

    
  );
}

export default App;
