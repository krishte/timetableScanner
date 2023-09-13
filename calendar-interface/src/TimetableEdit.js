import './App.css';
import React, { useState } from 'react';
import { LuEdit2 } from 'react-icons/lu';
import {BsCheckCircle, BsCheckCircleFill} from 'react-icons/bs';
import {GiArrowCursor} from 'react-icons/gi'
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
import Modal from 'react-bootstrap/Modal';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Image from 'react-bootstrap/Image';





function TimetableEdit(props) {

    //passed in properties from parent
//   const [croppedPos, setCroppedPos] = useState([[761, 242, 1517, 385], [1517, 242, 2101, 385], [2101, 242, 2469, 385], [2469, 242, 2677, 385], [2677, 242, 3174, 385], [3174, 242, 3392, 515], [153, 385, 602, 515], [761, 385, 1517, 515], [1517, 385, 2101, 515], [2101, 385, 2288, 515], [2288, 385, 2469, 515], [2677, 385, 2899, 515], [2899, 385, 3174, 515], [602, 385, 761, 826], [2469, 385, 2677, 826], [153, 515, 602, 669], [1094, 515, 1343, 669], [1517, 515, 1792, 669], [2677, 515, 3174, 669], [1343, 515, 1517, 826], [1792, 515, 1940, 826], [1940, 515, 2101, 826], [3174, 515, 3392, 826], [452, 669, 602, 826], [1094, 669, 1343, 826], [1517, 669, 1792, 826], [2101, 669, 2288, 826], [2288, 669, 2469, 826], [2677, 669, 3174, 826], [761, 669, 1094, 853], [260, 669, 452, 886], [153, 669, 260, 1143], [602, 886, 761, 1009], [761, 886, 1094, 1009], [1094, 886, 1343, 1009], [2101, 886, 2469, 1009], [2677, 886, 2899, 1009], [2899, 886, 3174, 1009], [3174, 886, 3392, 1009], [260, 886, 602, 1081], [1343, 886, 1517, 1143], [1517, 886, 1792, 1143], [2469, 886, 2677, 1143], [761, 1009, 934, 1143], [934, 1009, 1094, 1143], [2677, 1009, 3392, 1143], [1792, 1009, 2101, 1279], [1094, 1081, 1343, 1226], [153, 1143, 761, 1279], [761, 1143, 1094, 1279], [1343, 1143, 1517, 1279], [1517, 1143, 1792, 1279], [2101, 1143, 2288, 1279], [2288, 1143, 2469, 1279], [2677, 1143, 3392, 1279], [2469, 1143, 2677, 1392], [153, 1279, 761, 1392], [761, 1279, 1517, 1392]]);
//   const [summaries, setSummaries] = useState(["String Theory I Dr Ling Lin Mathematical Institute, L5", "Radiative processes and High Energy Astrophysics (C1) Dept Physics, Dennis Sciama Weeks 384", "String Theory | Dr Ling Lin Mathematical Institute, LS", "Astroparticle Physics Prof J Conlon Dept of Physics, Dennis Sciama", "Radiative processes and High Energy Astrophysics (C1) Dept Physics, Dennis Sciama Weeks 1-4", "Quantum Matter Prof Steve Simon Dept of Physics, Fisher room", "Advanced Fluid Dynamics Prof C Terquem and Prof Paul Dellar Dept of Physics, Lindemann", "Geophysical Fluid Dynamics (C5) Prof Tim Woollings Dept of Physics, Dennis Sciama Weeks 1-3", "\u20ac3.11 Riemannian Geometry Prof. Jason Lotay Mathematical Institute, L4", "Radiative processes and High Energy Astrophysics (C1) Dept of Physics, Dennis Sciama", "Collisionless Plasma Prof Plamen Ivanov Dept of Physics, Seminar room Weeks 2-5", "\u20ac3.11 Riemannian Geometry Prof. Jason Lotay Mathematical Institute, L4", "Geophysical Fluid Dynamics (C5} Prof Tim Woollings Dept of Physics, Dennis Sciama Weeks 1-3", "Quantum CMP Seminar 10.30-11.30 ALP Seminar 11.30-1", "Astro Grad Course 10-11.30 Plasma Seminar 11.30-1", "7.6 General Relativity Il Prof Christopher Couzens Mathematical Institute, L3", "Advanced Quantum Field Theory Dr Prateek Argawal Dept of Physics, Lindemann", "Supersymmetry and Supergravity Dr Christoph Uhlemann Mathematical Institute, L6", "C7.6 General Relativity II Prof Christopher Couzens Mathematical Institute, L3", "Solid and Liquid Crystals Seminar 11.00-13.00 Quantum Field Theory! Relativity 12.00-13.00 Seminar", "Cosmology Prof David Alonso Dept of Physics, Fisher Room", "Advanced Philosophy of Physics Prof Simon Saunders Merton College (Fitzjames 1)", "Soft Matter Physics Prof. Ard Louis Dept of Physics, Fisher Room", "Astroparticle Physics Prof J Conlon Dept of Physics, Lindemann", "Advanced Fluid Dynamics Prof C Terqum and Prof Paul Dellar Dept of Physics, Lindemann", "Radiative processes and High Energy Astrophysics (C1} Dept Physics, Dennis Sciama Weeks 5-8", "3.2 Geometric Group Theory Prof Cornelia Drutu Mathematical Institute, 13", "Industrial and Applied Mathematics Seminar Mathematical Institute, L1", "3.2 Geometric Group Theory Prof Cornelia Drutu Mathematical Institute, L3", "Quantum Field Theory Seminar (Weeks 2, 4, 6, 8) Mathematical Institute, L3", "String Theory Seminar Mathematical Institute, u", "Quantum CMP Seminar 10.30-11.30 ALP Seminar 11.30-1", "Astro Colloquium", "3.12 Low-Dimensional Topology and Knot Theory Prof. Andras Juhasz Mathematical Institute, L2", "Supersymmetry and Supergravity Dr Christoph Uhlemann Mathematical Institute, L1", "\u20ac3.12 Low-Dimensional Topology and Knot Theory Prof. Andras Juhasz Mathematical Institute, L4", "Fridays@2 Mathematical Institute, L1", "Theory Colloquium", "Mathematical Geoscience Seminar (Weeks 2, 4, 6, 8) Mathematical Institute, L4", "Geometry and Analysis Seminar Mathematical Institute, L4", "Galactic and Planetary Dynamics Prof John Magorrian Dept of Physics, Fisher room", "7.7 Random Matrix Theory Prof. Jon Keating Mathematical Institute, L3", "Advanced Quantum Field Theory Dr Prateek Argawal Dept of Physics, Lindemann", "Geometric Group Theory Seminar Mathematical Institute, L3", "Softbio Colloquium", "Collisionless Plasma Prof Plamen Ivanov, Dept of Physics, Fisher room Weeks 2-5", "Nonequilibrium Statistical Physics Prof. Ramin Golestanian Dept of Physics, Lindemann Weeks 1-4", "Random Matrix Theory Seminar Mathematical Institute, L\u00e9", "8.4 Probabilistic Combinatorics Prof Oliver Riordan Mathematical Institute, L3", "C5.6 Applied Complex Variables Prof Jon Chapman Mathematical Institute, L3", "Biophysics Seminar", "5.6 Applied Complex Variables Prof Jon Chapman Mathematical Institute, L3", "8.4 Probabilistic Combinatorics Prof Oliver Riordan Mathematical Institute, 13", "Particle Theory Seminar", "Fridays@4 Mathematical Institute, L1", "Nonequilibrium Statistical Physics Prof. Ramin Golestanian Dept of Physics, Lindemann Weeks 1-4", "C7.4 Introduction to Quantum Information Prof. Artur Ekert Mathematical Institute, L3.", "C7.4 Introduction to Quantum Information Prof. Artur Ekert Mathematical Institute, L3"]);
//   const [times, setTimes] = useState(['9:00-10:00', '9:00-10:00', '9:00-10:00', '9:00-10:00', '9:00-10:00', '9:00-11:00', '10:00-11:00', '10:00-11:00', '10:00-11:00', '10:00-11:00', '10:00-11:00', '10:00-11:00', '10:00-11:00', '10:00-13:00', '10:00-13:00', '11:00-12:00', '11:00-12:00', '11:00-12:00', '11:00-12:00', '11:00-13:00', '11:00-13:00', '11:00-13:00', '11:00-13:00', '12:00-13:00', '12:00-13:00', '12:00-13:00', '12:00-13:00', '12:00-13:00', '12:00-13:00', '12:00-13:30', '12:00-14:00', '12:00-16:00', '14:00-15:00', '14:00-15:00', '14:00-15:00', '14:00-15:00', '14:00-15:00', '14:00-15:00', '14:00-15:00', '14:00-15:30', '14:00-16:00', '14:00-16:00', '14:00-16:00', '15:00-16:00', '15:00-16:00', '15:00-16:00', '15:00-17:00', '15:30-16:30', '16:00-17:00', '16:00-17:00', '16:00-17:00', '16:00-17:00', '16:00-17:00', '16:00-17:00', '16:00-17:00', '16:00-18:00', '17:00-18:00', '17:00-18:00']);
//   const [days, setDays] = useState([['Tuesday'], ['Wednesday'], ['Thursday'], ['Thursday'], ['Friday'], ['Friday'], ['Monday'], ['Tuesday'], ['Wednesday'], ['Thursday'], ['Thursday'], ['Friday'], ['Friday'], ['Monday'], ['Thursday'], ['Monday'], ['Tuesday'], ['Wednesday'], ['Friday'], ['Tuesday'], ['Wednesday'], ['Wednesday'], ['Friday'], ['Monday'], ['Tuesday'], ['Wednesday'], ['Thursday'], ['Thursday'], ['Friday'], ['Tuesday'], ['Monday'], ['Monday'], ['Monday'], ['Tuesday'], ['Tuesday'], ['Thursday'], ['Friday'], ['Friday'], ['Friday'], ['Monday'], ['Tuesday'], ['Wednesday'], ['Thursday'], ['Tuesday'], ['Tuesday'], ['Friday'], ['Wednesday'], ['Tuesday'], ['Monday'], ['Tuesday'], ['Tuesday'], ['Wednesday'], ['Thursday'], ['Thursday'], ['Friday'], ['Thursday'], ['Monday'], ['Tuesday']]);
//   const [weeks, setWeeks] = useState([[], [384], [], [], [1, 2, 3, 4], [], [], [1, 2, 3], [], [], [2, 3, 4, 5], [], [1, 2, 3], [], [], [], [], [], [], [], [], [], [], [], [], [8, 5, 6, 7], [], [], [], [8, 2, 4, 6], [], [], [], [], [], [], [], [], [8, 2, 4, 6], [], [], [], [], [], [], [2, 3, 4, 5], [1, 2, 3, 4], [], [], [], [], [], [], [], [], [1, 2, 3, 4], [], []]);
    
    const [croppedPos, ] = useState(props.croppedPos);
    const [backgroundImg, ] = useState(props.backgroundImg)
    const [croppedURLs, ] = useState(props.croppedURLs)
    const [timeCroppedURLs, ] = useState(props.timeCroppedURLs);
    const [horizontalLines, ] = useState(props.horizontalLines);
    const [timeBoxes, setTimeBoxes] = useState(props.timeBoxes)
    const [events, ] = useState(props.events)
    

    const [summaries, setSummaries] = useState(null);
    const [times, setTimes]  = useState(null);
    const [days, setDays]  = useState(null);
    const [weeks, setWeeks] = useState(null);
  
  const daysofweek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  const [boxSelection, setBoxSelection] = useState(new Array(1000).fill(false));
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const [show, setShow] = useState(true);
  const [modalSummary, setModalSummary] = useState("");
  const [modalFirstTime, setModalFirstTime] = useState("");
  const [modalSecondTime, setModalSecondTime] = useState("");
  const [modalDays, setModalDays] = useState([]);
  const [modalWeeks, setModalWeeks] = useState("");
  const [downloaded, setDownloaded] = useState(false)

  const [editIndex, setEditIndex] = useState(null);

  const [justOpened, setJustOpened] = useState(true);
  const [editStage, setEditStage] = useState(1);



  const handleBoxClick = (index) => {
    const updatedSelection = [...boxSelection];
    updatedSelection[index] = !updatedSelection[index];
    setBoxSelection(updatedSelection)
  };

  const handleEditTimeClick = (index) => {
    const editTimes = timeBoxes[index][0].split('-')
    if (editTimes[0].length===4) {
      setModalFirstTime("0" + editTimes[0])
    }
    else {
      setModalFirstTime(editTimes[0]);
    }
    if (editTimes[1].length===4) {
      setModalSecondTime("0" + editTimes[1])
    }
    else {
      setModalSecondTime(editTimes[1]);
    }
    setEditIndex(index);
    setShow(true);
  }

  const handleEditClick = (index) => {
    const editTimes = times[index].split('-')
    setModalSummary(summaries[index]);
    if (editTimes[0].length===4) {
      setModalFirstTime("0" + editTimes[0])
    }
    else {
      setModalFirstTime(editTimes[0]);
    }
    if (editTimes[1].length===4) {
      setModalSecondTime("0" + editTimes[1])
    }
    else {
      setModalSecondTime(editTimes[1]);
    }
    setModalDays(days[index]);
    setModalWeeks(weeks[index].toString());
    setEditIndex(index);
    setShow(true);
  };

  const handleEditCancel = () => {
    setShow(false);
  }

  const isSmaller = (time1, time2) => {
    if (parseInt(time1.substring(0,2)) > parseInt(time2.substring(0,2))) {
      return false;
    }
    else if (parseInt(time1.substring(0,2)) === parseInt(time2.substring(0,2)) && parseInt(time1.substring(3,5)) >= parseInt(time2.substring(3,5))) {
      return false;
    }
    return true;
  }

  const handleEditTimeSave = () => {
    const updatedTimeBoxes = [...timeBoxes]
    updatedTimeBoxes[editIndex][0] = modalFirstTime+"-"+modalSecondTime
    setTimeBoxes(updatedTimeBoxes)
    setShow(false)
  }

  const handleEditSave = () => {
    if (modalSummary==="") {
      alert("Title cannot be empty")
      return;
    }
    else if (!isSmaller(modalFirstTime, modalSecondTime)) {
      alert("Start time must occur before End time")
      return;
    }
    const updatedDays = [...days]
    const updatedSummaries = [...summaries]
    const updatedTimes = [...times]
    const updatedWeeks = [...weeks]

    updatedDays[editIndex] = modalDays;
    updatedSummaries[editIndex] = modalSummary
    updatedTimes[editIndex] = modalFirstTime+"-"+modalSecondTime
    if (modalWeeks==="") {
      updatedWeeks[editIndex] = []
    }
    else {
      let specificWeeks= modalWeeks.split(',').map(function(e) { 
        e = parseInt(e) 
        return e;
      });

      for (var i = 0; i < specificWeeks.length; i++) {
        if (isNaN(specificWeeks[i])) {
          alert("Weeks format is incorrect");
          return;
        }
      }

      updatedWeeks[editIndex] = specificWeeks
    }
    setSummaries(updatedSummaries);
    setDays(updatedDays);
    setTimes(updatedTimes)
    setWeeks(updatedWeeks)

    setShow(false);
  }

  const handleModalClose = () => {
    setShow(false)
    setTimeout(() => {
      setJustOpened(false);    
    }, 100);
  }

  const handleMouseEnter = (index) => {
    setHoveredIndex(index);
  };

  const handleMouseLeave = () => {
    setHoveredIndex(null);
  };

  const handleEditDayClick = (dayIndex) => {
    const updatedModalDays = [...modalDays]
    if (modalDays.includes(daysofweek[dayIndex])) {
      updatedModalDays.splice(modalDays.indexOf(daysofweek[dayIndex]), 1)
    }
    else {
      updatedModalDays.push(daysofweek[dayIndex])
    }
    setModalDays(updatedModalDays)
  }

  const handleEditSummaryChange = (event) => {
    setModalSummary(event.target.value);
  }

  const handleEditFirstTimeChange = (event) => {
    setModalFirstTime(event.target.value)
  }

  const handleEditSecondTimeChange = (event) => {
    setModalSecondTime(event.target.value)
  }

  const handleEditWeeksChange = (event) => {
    setModalWeeks(event.target.value)
  }

  const handleDownloadClick = () => {
    const boxIndices = boxSelection.map((value, index) => (value === true ? index : -1)).filter(index => index !== -1);
    const dataToSend = [boxIndices.map(index => summaries[index]), boxIndices.map(index => days[index]), boxIndices.map(index => times[index]), boxIndices.map(index => weeks[index]), props.startDate, props.endDate]
    
    console.log("POSTing download")
    fetch('http://172.20.135.41:5001/createCalendarFile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.blob()
    }).then(blob => {
        const fileURL = window.URL.createObjectURL(blob);
        // Create a hidden <a> element to trigger the download
        const a = document.createElement('a');
        a.href = fileURL;
        a.download = 'timetable.ics'; // Set the desired filename

        // Trigger the download
        document.body.appendChild(a);
        a.click();

        // Clean up the URL and <a> element
        window.URL.revokeObjectURL(fileURL);
        document.body.removeChild(a);
        setDownloaded(true);
        setShow(true);
    })
    .catch(err => {
      console.log(err);
    })
  }

  const handleNextClick = () => {
    const dataToSend = [events, timeBoxes]
    console.log("POSTing recalculate times")
    fetch('http://172.20.135.41:5001/recalculateTimes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json()
    }).then(data => {
        setSummaries(data.summaries)
        setTimes(data.times)
        setDays(data.days)
        setWeeks(data.weeks)
        setEditStage(2);
    })
    .catch(err => {
      console.log(err);
    })
    
  }

  const renderEventTooltip = (props, index) => (
    <Tooltip id="button-tooltip" className='mytooltip'{...props}>
      <h5>{times[index]}</h5>
      <h6 style={{width:"300px"}}>{summaries[index]}</h6>
      <ButtonGroup  aria-label="First group">
        {daysofweek.map((item,index2) => {
          return (<Button key={index2.toString() + "daybutton" + index.toString()} variant={days[index].includes(item) ? "primary" : "secondary"}>{item.substring(0,1)}</Button>);
        })}
      </ButtonGroup>
      <h6 style={{paddingTop:"10px"}}>{weeks[index].toString() === "" ? "" : "Weeks: " + weeks[index].toString()}</h6>
    </Tooltip>
  );

  const renderTimeTooltip = (props, index) => (
    <Tooltip id="button-tooltip" className='mytooltip'{...props}>
      <h5>{timeBoxes[index][0]}</h5>
    </Tooltip>
  );

  let cropped_time_list = timeBoxes.map((item,index) => {
    return( 

      <div>
          <OverlayTrigger
            key={index.toString() + "overlayTime"}
            delay={{ show: 100, hide: 0 }}
            placement="auto-end"
            overlay={(props) => renderTimeTooltip(props, index)}
          >
            <Image key={index.toString()+"croppedTime"} src={timeCroppedURLs[index]}
              style={{position: 'absolute', top: horizontalLines[item[2]], left: item[1]}} 
              className="hover-zoom"      
              alt = "Loading..."
            />
          </OverlayTrigger>
          <Button key={index.toString() + "editcircle"} style={{position: 'absolute', top: (horizontalLines[item[2]]+horizontalLines[item[4]])/2-15, left: item[3]+15, zIndex:3}}  onClick={() => handleEditTimeClick(index)}  >
            <LuEdit2 key={index.toString() + "edit"} size="15px" color="white"/>
          </Button>
{/*          
          <Button key={index.toString() + "editcircle"} style={{position: 'absolute', top: item[3]-45, left: item[0]+15, zIndex:3}}  onClick={() => handleEditClick(index)}  >
            <LuEdit2 key={index.toString() + "edit"} size="15px" color="white"/>
          </Button> */}
      </div>
    );
  })

  let cropped_img_list = croppedPos.map((item,index)=>{
    let selection;
    if (boxSelection[index]) {
        selection = (
            <BsCheckCircleFill key={index.toString() + "checkfill"} style={{position: 'absolute', top: item[3]-38, left: item[2]-38, zIndex: 2}} size="30px" color="#149c58"/>
        );
    }
    else {
        selection=<BsCheckCircle key={index.toString() + "check"} style={{position: 'absolute', top: item[3]-38, left: item[2]-38, zIndex: 2}} size="30px"/>
    }
    return( 

      <div>
          <OverlayTrigger
            key={index.toString() + "overlay"}
            delay={{ show: 100, hide: 0 }}
            placement="auto-end"
            overlay={(props) => renderEventTooltip(props, index)}
          >
            <Image key={index.toString()+"croppedimage"} src={croppedURLs[index]}
              style={{position: 'absolute', top: item[1], left: item[0], opacity: boxSelection[index] ? 1.0 : (hoveredIndex===index ? 1:0.2)}} 
              className="hover-zoom"  
              onClick={() => handleBoxClick(index)}         
              onMouseEnter={() => handleMouseEnter(index)}
              onMouseLeave={handleMouseLeave}
              alt = "Loading..."
            />
          </OverlayTrigger>
          
          {/* <div style={{width:"30px", height:"30px", backgroundColor:"#2982f0", borderRadius: "50%", position:"absolute", top: item[3]-38, left:item[0]+22, zIndex:2}}/> */}
          <Button key={index.toString() + "editcircle"} style={{position: 'absolute', top: item[3]-45, left: item[0]+15, zIndex:3}}  onClick={() => handleEditClick(index)}  >
            <LuEdit2 key={index.toString() + "edit"} size="15px" color="white"/>
          </Button>

          {selection}
      </div>
    );
  })


  let modalContent;
  if (justOpened) {
    modalContent = (
      <Modal show={show} onHide={handleModalClose}>
        
        <Modal.Header>
          <Modal.Title>Instructions</Modal.Title>
        </Modal.Header>
          <Row style={{padding:"20px"}}>
            <Col xs={3} style={{textAlign:"center"}}>
              <GiArrowCursor size="40px" />
            </Col>
            <Col>Hover over an event to see the information found for that event</Col>
          </Row>
          <Row style={{padding:"20px"}}>
            <Col xs={3} style={{textAlign:"center"}}>
                <BsCheckCircleFill size="40px"  color="#149c58"  />
            </Col>
            <Col>Click on an event to include the event in the final downloaded file</Col>
          </Row>
          <Row style={{padding:"20px"}} >
            <Col xs={3} style={{textAlign:"center"}}>
            <Button style={{textAlign: "center"}} size="40px">
             <LuEdit2 />
             </Button>
            </Col>
            <Col> Click the edit button on an event to edit the information for that event</Col>
          </Row>

        <Modal.Footer>
          <Button variant="primary" onClick={handleModalClose}>
            OK
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
  else if (downloaded) {
    modalContent = (
      <Modal show={show} onHide={handleEditCancel}>
        <Modal.Header closeButton>
          <Modal.Title>Uploading to a Calendar Service</Modal.Title>
        </Modal.Header>
          <Form.Group as={Col} style={{padding:"15px"}} controlId="Google Calendar">
            <h5>Goole Calendar</h5>
            <a href="https://support.google.com/calendar/thread/3231927/how-do-i-import-ics-files-into-google-calendar?hl=en" target="_blank">Instructions</a>
          </Form.Group>

          <Form.Group as={Col} style={{padding:"15px"}} controlId="Apple Calendar">
            <h5>Apple Calendar</h5>
            <a href="https://www.lifewire.com/how-to-import-ics-calendar-files-in-ical-1172177#:~:text=Like%20Google%20Calendar%2C%20Apple%20Calendar,ICS%20file%20and%20click%20Import." target="_blank">Instructions</a>
          </Form.Group>

          <Form.Group as={Col} style={{padding:"15px"}} controlId="Outlook Calendar">
            <h5>Outlook Calendar</h5>
            <a href="https://support.microsoft.com/en-us/office/import-calendars-into-outlook-8e8364e1-400e-4c0f-a573-fe76b5a2d379" target="_blank">Instructions</a>
          </Form.Group>

        <Modal.Footer>
          <Button variant="primary" onClick={handleEditCancel}>
            OK
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
  else if (editStage===2) {
    modalContent = (
      <Modal show={show} onHide={handleEditCancel}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Event</Modal.Title>
        </Modal.Header>
        <Form.Group style={{padding:"10px"}} as={Col} controlId="eventTitle">
          <Form.Label>Title</Form.Label>
          <Form.Control 
            as="textarea" 
            value={modalSummary} 
            onChange={handleEditSummaryChange} 
            placeholder="Event title"
            style={{ height: '80px' }}
          />
        </Form.Group>
        <Row className="mb-3" style={{padding:"10px"}}>
          <Form.Group as={Col} controlId="startTime">
            <Form.Label>Start time</Form.Label>
            <Form.Control
              type="time"
              className="modalFirstDate"
              value={modalFirstTime}
              onChange={handleEditFirstTimeChange} 
            />            
          </Form.Group>

          <Form.Group as={Col} controlId="endTime">
            <Form.Label>End time</Form.Label>
            <Form.Control
              type="time"
              className="modalSecondDate"
              value={modalSecondTime}
              onChange={handleEditSecondTimeChange}
            />            
          </Form.Group>
        </Row>
        <Form.Group as={Col} controlId="eventDays" style={{padding:"10px"}}>
          <Form.Label>Days</Form.Label>
          <ButtonGroup  aria-label="First group" style={{width:"100%"}}>
            {daysofweek.map((item,index) => {
              return (
                <Button 
                  key={index.toString() + "editdaybutton"} 
                  variant={modalDays===null ? "secondary" : (modalDays.includes(item) ? "primary" : "secondary")}
                  onClick={() => handleEditDayClick(index)}
                >
                  {item.substring(0,1)} 
                </Button>
              );
            })}
          </ButtonGroup>
        </Form.Group>
        <Form.Group as={Col} controlId="eventWeeks" style={{padding:"10px"}}>
          <Form.Label>Weeks</Form.Label>
          <Form.Control 
            as="input" 
            value={modalWeeks} 
            onChange={handleEditWeeksChange} 
            placeholder="Specific weeks for which the event repeats"
          />
          <Form.Text className="text-muted">
            Separate week numbers by commas or leave blank to repeat all weeks
          </Form.Text>
        </Form.Group>

        <Modal.Footer>
          <Button variant="secondary" onClick={handleEditCancel}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleEditSave}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
  else {
    modalContent = (
      <Modal show={show} onHide={handleEditCancel}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Time</Modal.Title>
        </Modal.Header>
        <Row className="mb-3" style={{padding:"10px"}}>
          <Form.Group as={Col} controlId="startTime">
            <Form.Label>Start time</Form.Label>
            <Form.Control
              type="time"
              className="modalFirstDate"
              value={modalFirstTime}
              onChange={handleEditFirstTimeChange} 
            />            
          </Form.Group>

          <Form.Group as={Col} controlId="endTime">
            <Form.Label>End time</Form.Label>
            <Form.Control
              type="time"
              className="modalSecondDate"
              value={modalSecondTime}
              onChange={handleEditSecondTimeChange}
            />            
          </Form.Group>
        </Row>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleEditCancel}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleEditTimeSave}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }

  let currentCrop;
  if (editStage===1) {
    currentCrop = cropped_time_list;
  }
  else {
    currentCrop = cropped_img_list;
  }

  let changeButton;
  if (editStage===1) {
    changeButton = (
      <Button style={{position:'fixed', bottom: "50px", right: "50px", zIndex:3}} onClick={handleNextClick}>
          Next
      </Button>
    )
  }
  else {
    changeButton = (
      <Button style={{position:'fixed', bottom: "50px", right: "50px", zIndex:3}} onClick={handleDownloadClick}>
          Download file
      </Button>
    )
  }
 
 
  return (
    <div >
      <header>
        {changeButton}
        <Image src={URL.createObjectURL(backgroundImg)} style={{position: 'absolute', top: 0, left: 0, opacity: 0.2}} alt="hello :)" />
        {currentCrop}
        {modalContent}
      </header>
    </div>
  );
}

export default TimetableEdit;
