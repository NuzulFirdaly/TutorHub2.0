todoMain();

function todoMain() {
  const DEFAULT_OPTION = "Choose category";

  let inputElem = "Available",
    inputElem2= "Available",
    dateInput,
    timeInput,
    addButton,
    sortButton,
    tutor_id,
    todoList = [],
    calendar,
    shortlistBtn,
    changeBtn,
    todoTable;

  getElements();
  addListeners();
  initCalendar();
  load();
  renderRows(todoList);

  function getElements() {
    dateInput = document.getElementById("dateInput");
    timeInput = document.getElementById("timeInput");
    addButton = document.getElementById("addBtn");
    selectElem = document.getElementById("categoryFilter");
    changeBtn = document.getElementById("changeBtn");
    todoTable = document.getElementById("todoTable");
    tutor_id = document.getElementById("tutor_id").innerText;

  }
   //Adding the event to a list which isnt a persistent object i dont think.
    //Change this to a modal when a user click certain date.
  function addListeners() {
    addButton.addEventListener("click", addEntry, false);

    document.getElementById("todo-modal-close-btn").addEventListener("click", closeEditModalBox, false);

    changeBtn.addEventListener("click", commitEdit, false);
  }

  function addEntry(event) {

    let dateValue = dateInput.value;
    console.log("This is date:",dateValue)
    dateInput.value = ""; // reseting to empty

    let timeValue = timeInput.value;
    console.log("This is time:",timeValue)

    timeInput.value = "";
    if (dateValue ==="" || timeValue ==="") { //if statement to check if input is empty if empty alert, else save
        alert("Date or time input is empty");

    }else{
        let obj = {
              id: _uuid(),
              category: 'Available',
              date: dateValue,
              time: timeValue,
              done: false,
            };
            renderRow(obj);

            todoList.push(obj);

            save();
            console.log("This is object",obj);
            //every add entry submit to flask using the route, and then add to db

        }
  }

  function save() {
    console.log(tutor_id);
    calendarobject = {[tutor_id]:todoList} //need bracket for the variable-key because idky but it works
    let stringified = JSON.stringify(todoList);
    localStorage.setItem("todoList", stringified);
    fetch("/myschedule/submit_entry",{
                method :"POST",
                credentials: "include", //include cookies
                body: JSON.stringify(calendarobject),
                cache: "no-cache",
                headers: new Headers({
                    "content-type": "application/json"
                })

            });
  }

  function load() {
  //add a code here where retrieve todolist from flask and set inside local storage
  //https://www.youtube.com/watch?v=Oive66jrwBs
  console.log("==== Loading ====")
    fetch("/myschedule/fetch/"+tutor_id)
    .then(function(response){
        console.log("responce:",response.clone().json())
        return response.clone().json()
    })
    .then(function(data){
    console.log("data",data)
    //    let retrieved = localStorage.getItem("todoList");
    //    todoList = JSON.parse(retrieved);
    todoList = data
    console.log("list from local",todoList)
    //console.log(typeof todoList)
    console.log("this is the current todoList",todoList)
    renderRows(todoList);
    })
   console.log("==== FInished ====")

  }

  function renderRows(arr) {
    arr.forEach(todoObj => {
        console.log("rendering",todoObj);
      renderRow(todoObj);
    })
  }

  function renderRow({category: inputValue2, id, date, time, done }) {
    // add a new row

    let table = document.getElementById("todoTable");

    let trElem = document.createElement("tr");
    table.appendChild(trElem);

    // date cell
    let dateElem = document.createElement("td");

    dateElem.innerText = formatDate(date);
    trElem.appendChild(dateElem);

    // time cell
    let timeElem = document.createElement("td");
    timeElem.innerText = time;
    trElem.appendChild(timeElem);

    // category cell
    let tdElem3 = document.createElement("td");
    tdElem3.innerText = inputValue2;
    tdElem3.className = "categoryCell";
    trElem.appendChild(tdElem3);

    // edit cell
    let editSpan = document.createElement("span");
    editSpan.innerText = "edit";
    editSpan.className = "material-icons";
    editSpan.addEventListener("click", toEditItem, false);
    editSpan.dataset.id = id;
    let editTd = document.createElement("td");
    editTd.appendChild(editSpan);
    trElem.appendChild(editTd);


    // delete cell
    let spanElem = document.createElement("span");
    spanElem.innerText = "delete";
    spanElem.className = "material-icons";
    spanElem.addEventListener("click", deleteItem, false);
    spanElem.dataset.id = id;
    let tdElem4 = document.createElement("td");
    tdElem4.appendChild(spanElem);
    trElem.appendChild(tdElem4);
    //add to calendar
    addEvent({
      id: id,
      title: inputValue2,
      start: date,
    });

    dateElem.dataset.type = "date";
    dateElem.dataset.value = date;
    timeElem.dataset.type = "time";

    dateElem.dataset.id = id;
    timeElem.dataset.id = id;

    function deleteItem() {
      trElem.remove();

      for (let i = 0; i < todoList.length; i++) {
        if (todoList[i].id == this.dataset.id)
          todoList.splice(i, 1);
      }
      save();

      // remove from calendar
      calendar.getEventById( this.dataset.id ).remove();
    }

    function checkboxClickCallback() {
      trElem.classList.toggle("strike");
      for (let i = 0; i < todoList.length; i++) {
        if (todoList[i].id == this.dataset.id)
          todoList[i]["done"] = this.checked;
      }
      save();
    }

  }

  function _uuid() {
    var d = Date.now();
    if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
      d += performance.now(); //use high-precision timer if available
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = (d + Math.random() * 16) % 16 | 0;
      d = Math.floor(d / 16);
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
  }

  function sortEntry() {
    todoList.sort((a, b) => {
      let aDate = Date.parse(a.date);
      let bDate = Date.parse(b.date);
      return aDate - bDate;
    });

    save();

    clearTable();

    renderRows(todoList);
  }

  function initCalendar() {
    var calendarEl = document.getElementById('calendar');

    calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      initialDate: '2021-02-12',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      events: [],
      eventClick: function(info) {
        toEditItem(info.event);
      },
      eventBackgroundColor: "#378006",
      eventBorderColor: "#378006",
    });

    calendar.render();
  }

  function addEvent(event){
    calendar.addEvent( event );
  }

  function clearTable(){
    // Empty the table, keeping the first row
    let trElems = document.getElementsByTagName("tr");
    for (let i = trElems.length - 1; i > 0; i--) {
      trElems[i].remove();
    }

    calendar.getEvents().forEach(event=>event.remove());
  }


  function onTableClicked(event){
    if(event.target.matches("td") && event.target.dataset.editable == "true"){
      let tempInputElem;
      switch(event.target.dataset.type){
        case "date" :
          tempInputElem = document.createElement("input");
          tempInputElem.type = "date";
          tempInputElem.value = event.target.dataset.value;
          break;
        case "time" :
          tempInputElem = document.createElement("input");
          tempInputElem.type = "time";
          tempInputElem.value = event.target.innerText;
          break;
        case "category" :
          tempInputElem = document.createElement("input");
          tempInputElem.value = event.target.innerText;

          break;
        default:
      }
      event.target.innerText = "";
      event.target.appendChild(tempInputElem);

      tempInputElem.addEventListener("change", onChange, false);


    }

    function onChange(event){
      let changedValue = event.target.value;
      let id = event.target.parentNode.dataset.id;
      let type = event.target.parentNode.dataset.type;

      // remove from calendar
      calendar.getEventById( id ).remove();

      todoList.forEach( todoObj => {
        if(todoObj.id == id){
          //todoObj.todo = changedValue;
          todoObj[type] = changedValue;

          addEvent({
            id: id,
            title: changedValue,
            start: todoObj.date,
          });
        }
      });
      save();

      if(type == "date"){
        event.target.parentNode.innerText = formatDate(changedValue);
      }else{
        event.target.parentNode.innerText = changedValue;
      }

    }
  }

  function formatDate(date){
    let dateObj = new Date(date);
    let formattedDate = dateObj.toLocaleString("en-GB", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
    return formattedDate;
  }

  function showEditModalBox(event){
    document.getElementById("todo-overlay").classList.add("slidedIntoView");
  }

  function closeEditModalBox(event){
    document.getElementById("todo-overlay").classList.remove("slidedIntoView");
  }

  function commitEdit(event){
    closeEditModalBox();

    let id = event.target.dataset.id;
    let category = document.getElementById("todo-edit-category").value;
    let date = document.getElementById("todo-edit-date").value;
    let time = document.getElementById("todo-edit-time").value;

    // remove from calendar
    calendar.getEventById( id ).remove();

    for( let i = 0; i < todoList.length; i++){
      if(todoList[i].id == id){
        todoList[i] = {
          id  : id,
          category : category,
          date : date,
          time : time
        };

        addEvent({
          id: id,
          title: category,
          start: todoList[i].date,
        });
      }
    }

    save();

    // Update the table
    let tdNodeList = todoTable.querySelectorAll("td");
    for(let i = 0; i < tdNodeList.length; i++){
      if(tdNodeList[i].dataset.id == id){
        let type = tdNodeList[i].dataset.type;
        switch(type){
          case "date" :
            tdNodeList[i].innerText = formatDate(date);
            break;
          case "time" :
            tdNodeList[i].innerText = time;
            break;
          case "category" :
            tdNodeList[i].innerText = category;
            break;
        }
      }
    }
  }

  function toEditItem(event){
    showEditModalBox();

    let id;

    if(event.target) // mouse event
      id = event.target.dataset.id;
    else // calendar event
      id = event.id;

    preFillEditForm(id);
  }

  function preFillEditForm(id){
    let result = todoList.find(todoObj => todoObj.id == id);
    let {category, date, time} = result;

    document.getElementById("todo-edit-category").value = category;
    document.getElementById("todo-edit-date").value = date;
    document.getElementById("todo-edit-time").value = time;

    changeBtn.dataset.id = id;
  }

}