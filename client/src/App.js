import './App.css';
import React, { useState } from 'react';
import TimetableEdit from './TimetableEdit';
import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image';
import Spinner from 'react-bootstrap/Spinner';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import InputGroup from 'react-bootstrap/InputGroup';
import Stack from 'react-bootstrap/Stack';
import 'react-18-image-lightbox/style.css';
import Lightbox from 'react-18-image-lightbox';
import timetable1 from "./assets/timetable1.png"
import timetable2 from "./assets/timetable2.jpg"
import timetable3 from "./assets/timetable3.jpg"
import timetable4 from "./assets/timetable4.png"
import timetable5 from "./assets/timetable5.png"
import {AiOutlinePlus} from "react-icons/ai";
import {BsCalendar3} from "react-icons/bs"
import timetable6 from "./assets/timetable6.jpg"


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
  const [errorTimes, setErrorTimes] = useState(null);



  const [timetableImgIndex, setTimetableImgIndex] = useState(0);
  const [fullscreenTimetable, setFullscreenTimetable] = useState(false);
  const [hoverIndex, setHoverIndex] = useState(-1);

  const timetableImgs = [timetable1, timetable2, timetable3, timetable4, timetable5, timetable6]
  

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
    fetch(process.env.NODE_ENV === 'production' ? 'http://timetablescan.com:5000/resizeImage' : 'http://127.0.0.1:5000/resizeImage', {
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
    fetch(process.env.NODE_ENV === 'production' ? 'http://timetablescan.com:5000/processTimetable' : 'http://127.0.0.1:5000/processTimetable' , {
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
        setErrorTimes(data.errorTimes)
        setEvents(data.events)
        console.log(data.errorTimes)
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

  const handleTimetableImgClick = (index) => {
    setTimetableImgIndex(index)
    console.log(index)
    setFullscreenTimetable(true)
  }

  const handleMouseEnter = (index) => {
    setHoverIndex(index)
  }

  const handleMouseLeave = () => {
    setHoverIndex(-1);
  }
  let uploadPreview = (
    <div  style={{paddingTop:"30px"}}>
      
      <Stack direction="horizontal" style={{padding:"30px"}} gap={3} className='stack border-secondary border rounded-3 bg-secondary-subtle'>
        {
          timetableImgs.map((item, index) => {
            return (
              <div 
                style={{position:"relative", textAlign:"center"}}
                onMouseEnter={() => handleMouseEnter(index)}
                onMouseLeave={handleMouseLeave}  
                className="timetable-img" 
                onClick={() => handleTimetableImgClick(index)}
              >
                <Image src={item}  width={300} />
                {hoverIndex===index && 
                  <div className='centered'>
                    <AiOutlinePlus />
                  </div>
                }
              </div>
            )
          })
        }
    </Stack>
    </div>
  )
  if (uploadedFile) {
    uploadPreview = (
      <Form.Group  style={{padding: "30px", position:"relative", textAlign:"center"}}>
        <Image src={URL.createObjectURL(uploadedFile)} style={{opacity:(loading ? 0.5:1.0) }} fluid/>
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
        errorTimes={errorTimes}
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
        <Row>
          <Col xs={1}  style={{position:"relative", textAlign:"center", padding:"20px"}}>
            <BsCalendar3 color="blue" style={{width:"100%", height:"100%"}}/>
          </Col>
          <Col xs={11} sm={11} md={8} lg={6} xl={6} style={{padding:"20px"}}>
            <p>This free online timetable scanner allows you to transfer information directly from a timetable to your preferred calendar service via an ics file. Below are some examples of images that this program will work on. Upload a PNG of JPEG to get started.</p>
          </Col>
        </Row>
        <div className='border-secondary border rounded-3 shadow bg-secondary-subtle' >
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
    <div>
      {fullscreenTimetable && (
        <Lightbox
          mainSrc={timetableImgs[timetableImgIndex]}
          nextSrc={timetableImgs[(timetableImgIndex + 1) % timetableImgs.length]}
          prevSrc={timetableImgs[(timetableImgIndex + timetableImgs.length - 1) % timetableImgs.length]}
          onCloseRequest={() => setFullscreenTimetable(false)}
          onMovePrevRequest={() => setTimetableImgIndex((timetableImgIndex + timetableImgs.length - 1) % timetableImgs.length)}
          onMoveNextRequest={() => setTimetableImgIndex((timetableImgIndex + 1) % timetableImgs.length)}
        />
      )}
    <Container fluid="md" style={{padding:"30px"}}>
      {currentView}
    </Container>

    </div>
  );
}

export default App;
