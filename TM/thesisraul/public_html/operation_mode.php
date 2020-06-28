<?php
ob_start();
session_start();

// Debug errors
#ini_set("display_errors", 1);
#error_reporting(E_ALL);

if (isset($_POST['name-id']) or isset($_POST['email'])) {

   include("../conf/settings.php");
   $dbconnection = mysqli_connect($host, $username, $password, $db_name);
   unset($host, $username, $password, $db_name);

   if (!$dbconnection) {
      die("CONNECTION FAILED: " . $dbconnection->mysqli_connect_error());
   }
?>
   <!DOCTYPE html>
   <html>

   <head>
      <title>MCHE Teacher request</title>
      <meta name="viewport" content="width = device-width, initial-scale = 1">
      <link rel="shortcut icon" type="image/x-icon" href="img/mche.ico" />
      <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
      <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
   </head>

   <body class="container">
      <div class="col s12 m12 l6">
         <div class="card-panel">
            <!-- Nav and info-->
            <nav class="navbar-fixed">
               <div class="nav-wrapper center-align">
                  <h3><?php echo ucfirst($_POST['mode']); ?> request</h3>
               </div>
            </nav>
            <!-- Request form-->
            <form class="col s12 m12 l6" action="request.php" method="POST" id="request-form-op">
               <div class="card-panel">
                  <!-- Teacher Information-->
                  <input value="Teacher Information" type="text" disabled />
                  <div class="row">
                     <div class="input-field col s6">
                        <i class="material-icons prefix">verified_user</i>
                        <input disabled type='text' value="<?php echo $_POST["name-id"]; ?>" />
                     </div>
                     <div class="input-field col s6">
                        <i class="material-icons prefix">email</i>
                        <input disabled type="email" value="<?php echo $_POST['email']; ?>">
                     </div>
                  </div>
                  <div class="row">
                     <div class="input-field col s6">
                        <i class="material-icons prefix">account_circle</i>
                        <input disabled type="text" value="<?php echo $_POST['firstName']; ?>">
                     </div>
                     <div class="input-field col s6">
                        <i class="material-icons prefix">account_circle</i>
                        <input disabled type="text" value="<?php echo $_POST['surname']; ?>">
                     </div>
                  </div>
                  <div class="row">
                     <div class="input-field col s6">
                        <i class="material-icons prefix">home</i>
                        <input disabled type="text" value="<?php echo $_POST['home']; ?>" />
                     </div>
                     <div class="input-field col s6">
                        <i class="material-icons prefix">label</i>
                        <input disabled type="text" value="<?php echo $_POST['department']; ?>" />
                     </div>
                  </div>
                  <div class="row">
                     <div class="input-field col s6" title="Your role for requesting the service">
                        <h6>Teacher Role</h6>
                        <p><label>
                              <input disabled checked class="actionmode" type="radio" />
                              <span>
                                 <?php
                                 if ($_POST['role'] == "ldteacher") {
                                    echo "Leading Teacher";
                                 } else {
                                    echo "Secondary School Teacher";
                                 }
                                 ?></span>
                           </label></p>
                     </div>
                  </div>
               </div>

               <?php
               // Save posted data into a session variable.
               $_SESSION['name-id'] = $_POST['name-id'];
               $_SESSION['email'] = $_POST['email'];
               $_SESSION['home'] = $_POST['home'];
               $_SESSION['department'] = $_POST['department'];
               $_SESSION['role'] = $_POST['role'];
               $_SESSION['mode'] = $_POST['mode'];
               $_SESSION['firstName'] = $_POST['firstName'];
               $_SESSION['surname'] = $_POST['surname'];

               // CREATE AND MODIFY MODE
               if ($_SESSION['mode'] == "create" || $_SESSION['mode'] == "modify") {
                  if ($_SESSION['mode'] == "create") {
               ?>
                     <script type="text/javascript">
                        window.addEventListener('load', function() {
                           document.getElementById("mainsubmit").style.display = 'block';
                           document.getElementById("modifyRequestDiv").style.display = 'block';
                        });
                     </script>
                  <?php
                  } elseif ($_SESSION['mode'] == "modify") {
                  ?>
                     <!-- Select your request to modify-->
                     <div id="modifyreq" class="card-panel">
                        <input value="Select request to modify" type="text" disabled />
                        <!-- Your requests -->
                        <div class="row">
                           <div class="input-field col s12 center" id="appenderror">
                              <?php
                              $id = $_SESSION['name-id'];
                              $query = "SELECT uuid FROM tmrequests WHERE id = '$id';";
                              $result = mysqli_query($dbconnection, $query) or die(mysqli_error($dbconnection));

                              if (mysqli_num_rows($result) == 0) {
                              ?>
                                 <form action="index.php" method="get">
                                    <p>There is no previous request made by the entered ID. Go back to the main page and create a new one.</p>
                                    <button type="submit" id="myButton" class="btn waves-effect waves-light">Home</button>
                                 </form>
                              <?php
                              } else {
                              ?>
                                 <h6>Your requests UUIDs</h6>
                                 <?php

                                 while ($rows = mysqli_fetch_array($result, MYSQLI_NUM)) {
                                 ?>
                                    <p><label>
                                          <input name="requestToModify" type="radio" value="<?php echo $rows[0]; ?>" />
                                          <span><?php echo $rows[0]; ?></span>
                                       </label></p>
                                 <?php
                                 }
                                 ?>
                                 <button onclick="showModifyForm()" class="btn waves-effect waves-light" type="button" name="modifyaction">Modify
                                    <i class="material-icons right">mode_edit</i>
                                 </button>
                              <?php
                              }
                              ?>
                           </div>
                        </div>
                     </div>
                     <script>
                        function showModifyForm() {
                           var x = document.querySelector('input[name="requestToModify"]:checked').value;
                           document.getElementById('modifyRequestDiv').innerHTML += '<input id="UUIDselected" type="hidden" name="UUIDselected" value="' + x + '"/>';
                           document.getElementById("modifyreq").style.display = 'none';
                           document.getElementById("mainsubmit").style.display = 'block';
                           document.getElementById("modifyRequestDiv").style.display = 'block';
                        }
                     </script>
                  <?php
                  }
                  ?>
                  <!-- Operation mode -->
                  <div id="modifyRequestDiv" style="display: none;">
                     <div class="card-panel">
                        <input value="Operation Mode" type="text" disabled />
                        <div class="row">
                           <div class="input-field col s6">
                              <h6>Action</h6>
                              <p><label><input disabled checked class="actionmode" type="radio" /><span>Create</span></label></p>
                           </div>
                           <div class="input-field col s6">
                              <h6 title="For how long do you want the service to be operational?">Service duration</h6>
                              <p title="For a defined period of time"><label><input onclick="createDatePeriod()" name="spec" id="defined" type="radio" value="defined" /><span>Defined</span></label></p>
                              <p title="For an indefinite period of time"><label><input onclick="hideDatediv()" name="spec" id="undefined" type="radio" value="undefined" /><span>Undefined</span></label></p>
                           </div>
                        </div>
                        <div id="datePeriod" class="row"></div>
                     </div>
                     <script>
                        var controlvar = false;
                        var controlvardiv = false;

                        function createDatePeriod() {
                           if (controlvardiv == false) {
                              document.getElementById("datePeriod").style.display = 'block';
                              document.getElementById("datePeriod").innerHTML +=
                                 '<div id="dateNew" class="input-field col s4" title="Date you want to have the service at your disposal"><i class="material-icons prefix">date_range</i><input id="start-date" name="start-date" type="text" class="datepicker" /><label for="start-date">Start date</label></div><div id="durationNew" class="input-field col s4" title="How many days do you want the service to be active?"><i class="material-icons prefix">access_time</i><input id="duration" name="duration" type="number" min="0" max="35" /><label for="duration">Duration (days)</label></div>';
                           }
                           const elems2 = document.querySelectorAll('.datepicker');
                           var options = {
                              format: 'dd-mm-yyyy'
                           };
                           for (element of elems2) {
                              M.Datepicker.init(element, options)
                           }
                           controlvar = false;
                           controlvardiv = true;
                        }

                        function hideDatediv() {
                           controlvar = false;
                           controlvardiv = false;
                           var datePeriodDiv = document.getElementById('datePeriodNew');
                           if (typeof(datePeriodDiv) != undefined && typeof(datePeriodDiv) != null && typeof(
                                 datePeriodDiv) != 'undefined') {
                              document.getElementById("dateNew").remove();
                              document.getElementById("durationNew").remove();
                           }
                        }
                     </script>


                     <!-- Service Details-->
                     <div class="card-panel">
                        <input value="Service Details" type="text" disabled />

                        <!-- Machine size and lesson type-->
                        <div class="row">
                           <div class="input-field col s6">
                              <h6 title="General field of lessons">Lessons Type</h6>
                              <p><label>
                                    <input name="lessontype" id="it" type="radio" value="it" onclick="showtopics(this.id)" />
                                    <span>IT</span>
                                 </label></p>
                              <p><label>
                                    <input name="lessontype" id="maths" type="radio" value="maths" onclick="showtopics(this.id)" />
                                    <span>Maths</span>
                                 </label></p>
                              <p><label>
                                    <input name="lessontype" id="biology" type="radio" value="biology" onclick="showtopics(this.id)" />
                                    <span>Biology</span>
                                 </label></p>
                              <p><label>
                                    <input name="lessontype" id="physics" type="radio" value="physics" onclick="showtopics(this.id)" />
                                    <span>Physics</span>
                                 </label></p>
                           </div>
                           <script type="text/javascript">
                              function showtopics(clicked_id) {
                                 var i;
                                 var dict = {
                                    "it": ["Networking", "Cybersecurity", "Programming", "Operating Systems", "Neural Networks"],
                                    "biology": ["Population Genetics", "Cell biology", "Applied Bioinformatics", "Biomechanics", "Reactions"],
                                    "maths": ["Graphs Theory", "Linear Algebra", "Mathematics Introduction", "Calculus", "Complex Numbers"],
                                    "physics": ["Quantum Mechanics", "Astrophysical Simulations", "Fluid Dynamics", "Applied Thermodynamics", "Aerodynamics Hydrodynamics"]
                                 };
                                 if (document.contains(document.getElementById("lessontypeSpec"))) {
                                    document.getElementById("lessontypeSpec").remove();
                                 }

                                 document.getElementById("lessontypeID").innerHTML +=
                                    '<div id="lessontypeSpec" class="input-field col s6"><h6 title="Specific topic of the lessons">Lesson topic</h6>';

                                 for (var key in dict) {
                                    if (key == clicked_id) {
                                       var topickey = key;
                                       var topicdict = dict[key];
                                    }
                                 }
                                 for (i = 0; i < topicdict.length; i++) {
                                    if (topicdict[i].indexOf(' ') >= 0) {
                                       var temp = topicdict[i].replace(/\s/g, "");
                                    } else {
                                       var temp = topicdict[i];
                                    }

                                    document.getElementById("lessontypeSpec").innerHTML +=
                                       '<p><label><input name="lessontopic" id="' + temp + '" type="radio" value="' + temp + '" /><span>' + topicdict[i] + '</span></label></p>';
                                 }
                                 document.getElementById("lessontypeSpec").innerHTML +=
                                    '</div>';
                              }
                           </script>
                           <div id="lessontypeID"></div>
                        </div>

                        <!-- Lessons difficulty and lesson type-->
                        <div class="row">
                           <div class="input-field col s6">
                              <h6 title="Select the service size">Service Size</h6>
                              <p><label>
                                    <input checked name="servicesize" id="small" type="radio" value="small" />
                                    <span>Small</span>
                                 </label></p>
                              <p><label>
                                    <input name="servicesize" id="medium" type="radio" value="medium" />
                                    <span>Medium</span>
                                 </label></p>
                              <p><label>
                                    <input name="servicesize" id="large" type="radio" value="large" />
                                    <span>Large</span>
                                 </label></p>
                           </div>
                           <div class="input-field col s6">
                              <h6>Home directories</h6>
                              <p><label>
                                    <input checked name="homedirectories" id="mche" type="radio" value="mche" />
                                    <span>MCHE</span>
                                 </label></p>
                              <p><label>
                                    <input name="homedirectories" id="home" type="radio" value="home" />
                                    <span><?php echo $_POST['home']; ?></span>
                                 </label></p>
                           </div>
                        </div>
                     </div>

                     <!-- Users Details-->
                     <div class="card-panel">
                        <input value="Users Details" type="text" disabled />
                        <h6>Create new users</h6>
                        <p>
                           <div class="row" id="createbtn">
                              <div class="input-field col s3">
                                 <i class="material-icons prefix">account_circle</i>
                                 <label for="numberstudents">Number of users</label>
                                 <input id="numberstudents" name="numberstudents" type="number" />
                              </div>
                              <div class="input-field col s6">
                                 <a class="waves-effect waves-light btn" onclick="createUsers()">Create</a>
                                 <script type="text/javascript">
                                    function createUsers() {
                                       var count = document.getElementById("numberstudents").value;
                                       document.getElementById("createbtn").style.display = 'none';
                                       var tmp = 0;
                                       while (count--) {
                                          tmp++;
                                          document.getElementById("usersfield").innerHTML +=
                                             "<div class='input-field col s3'><i class='material-icons prefix'>account_circle</i><label for='user" +
                                             tmp + "'>User " + tmp + "</label><input id='user" + tmp +
                                             "' name='user" +
                                             tmp + "' type='text'/></div>";
                                       }
                                    }
                                 </script>
                              </div>
                           </div>
                        </p>
                        <div class="row">
                           <div id="usersfield"></div>
                        </div>

                        <!-- Cooperation mode -->
                        <div class="row">
                           <div class="input-field col s3">
                              <h6>Cooperation mode</h6>
                              <p><label>
                                    <input checked onclick="hideNumGroups()" name="coopmode" id="isolated" type="radio" value="isolated" />
                                    <span>Isolated</span>
                                 </label></p>
                              <p><label>
                                    <input onclick="numberGroups()" name="coopmode" id="groups" type="radio" value="groups" />
                                    <span>Groups</span>
                                 </label></p>
                              <p><label>
                                    <input onclick="hideNumGroups()" name="coopmode" id="common" type="radio" value="common" />
                                    <span>Common</span>
                                 </label></p>
                              <script type="text/javascript">
                                 var cntrlvar = false;

                                 function numberGroups() {
                                    if (cntrlvar == false) {
                                       document.getElementById("numberGroupsrow").style.display = 'block';
                                       document.getElementById("numberGroupsrow").innerHTML +=
                                          '<div id="enterNumGroupDiv"><h6>Create new groups</h6><p><div class="input-field col s4"><i class="material-icons prefix">groups</i><label for="numgroupsrange">Number of groups</label><input id="numgroupsrange" name="numgroupsrange" type="number" min="1" max="6" required /></div></p></div><div id="enterNumGroupButton" class="input-field col s1"><a class="waves-effect waves-light btn" onclick="createGroups()">Create</a></div>';
                                    }
                                    cntrlvar = true;
                                 }

                                 function createGroups() {
                                    var count = document.getElementById("numgroupsrange").value;
                                    document.getElementById("numberGroupsrow").style.display = 'none';
                                    var tmp = 0;
                                    document.getElementById("enterGroups").innerHTML +=
                                       "<div id='enterGroupsNamesDiv'><h6>Insert users separated by commas</h6><p>";
                                    while (count--) {
                                       tmp++;
                                       if (tmp == 1) {
                                          document.getElementById("enterGroupsNamesDiv").innerHTML +=
                                             "<div class='input-field col s3'><i class='material-icons prefix'>groups</i><input id='group" +
                                             tmp +
                                             "' name='group" + tmp +
                                             "' type='text'/><label for='group" +
                                             tmp + "'>Group " + tmp +
                                             "</label><span class='helper-text'>user1, user2 ...</span></div>";
                                       } else {
                                          document.getElementById("enterGroupsNamesDiv").innerHTML +=
                                             "<div class='input-field col s3'><i class='material-icons prefix'>groups</i><input id='group" +
                                             tmp +
                                             "' name='group" + tmp +
                                             "' type='text'/><label for='group" +
                                             tmp + "'>Group " + tmp + "</label></div>";
                                       }
                                    }
                                    document.getElementById("enterGroupsNamesDiv").innerHTML += "</p></div>";
                                    cntrlvar = true;
                                 }

                                 function hideNumGroups() {
                                    cntrlvar = false;
                                    var enterNumGroups = document.getElementById('enterNumGroupDiv');
                                    var enterGroupsNames = document.getElementById('enterGroupsNamesDiv');
                                    if (typeof(enterNumGroups) != undefined && typeof(enterNumGroups) !=
                                       null &&
                                       typeof(
                                          enterNumGroups) !=
                                       'undefined') {
                                       document.getElementById("enterNumGroupDiv").remove();
                                       document.getElementById("enterNumGroupButton").remove();
                                    }
                                    if (typeof(enterGroupsNames) != undefined && typeof(enterGroupsNames) !=
                                       null &&
                                       typeof(enterGroupsNames) != 'undefined') {
                                       document.getElementById('enterGroupsNamesDiv').remove();
                                    }
                                 }
                              </script>
                           </div>
                           <div id="numberGroupsrow" class="input-field col s9"></div>
                           <div id="enterGroups" class="input-field col s9"></div>
                        </div>
                     </div>

                     <!-- Additional Details -->
                     <div class="card-panel">
                        <input value="Additional Details" type="text" disabled />
                        <div class="row">
                           <div class="input-field col s6">
                              <h6>What do you want to keep?</h6>
                              <p><label>
                                    <input type="checkbox" id="userData" name="WhatPersistedItems[]" value="user_data" />
                                    <span>User Data</span>
                                 </label></p>
                              <p><label>
                                    <input type="checkbox" id="userStatistics" name="WhatPersistedItems[]" value="user_stats" />
                                    <span>User Statistics</span>
                                 </label></p>
                           </div>
                           <div class="input-field col s6">
                              <h6>Additional services</h6>
                              <p><label>
                                    <input type="checkbox" id="sshCheck" name="additionalservices[]" value="ssh" />
                                    <span>SSH Access</span>
                                 </label></p>
                              <p><label>
                                    <input type="checkbox" id="webCheck" name="additionalservices[]" value="web" />
                                    <span>Web Interface</span>
                                 </label></p>
                           </div>
                        </div>
                     </div>
                  </div>

               <?php
                  // DELETE MODE
               } elseif ($_SESSION['mode'] == "delete") {
               ?>
                  <script>
                     document.getElementById("formsubmitmain").style.display = 'none';
                  </script>
                  <form action="request.php" method="POST">
                     <!-- Select your request to delete-->
                     <div class="card-panel" id="deleterequest">
                        <input value="Select request to delete" type="text" disabled />
                        <!-- Your requests -->
                        <div class="row">
                           <div class="input-field col s12 center">
                              <?php
                              $id = $_SESSION['name-id'];
                              $query = "SELECT uuid FROM tmrequests WHERE id = '$id';";
                              $result = mysqli_query($dbconnection, $query) or die(mysqli_error($dbconnection));
                              if (mysqli_num_rows($result) == 0) {
                              ?>
                                 <form action="index.php" method="get">
                                    <p>There is no previous request made by the entered ID. Go back to the main page and create a new one.</p>
                                    <button type="submit" id="myButton" class="btn waves-effect waves-light">Home</button>
                                 </form>
                              <?php
                              } else {
                              ?>
                                 <h6>Your requests UUIDs</h6>
                                 <?php
                                 while ($rows = mysqli_fetch_array($result, MYSQLI_NUM)) {

                                 ?>
                                    <p><label>
                                          <input name="requestToDelete" type="radio" value="<?php echo $rows[0]; ?>" />
                                          <span><?php echo $rows[0]; ?></span>
                                       </label></p>

                                 <?php
                                 }
                                 ?>
                                 <button onclick="showDeleteForm()" class="btn waves-effect waves-light" type="button" name="modifyaction">Delete
                                    <i class="material-icons right">delete</i>
                                 </button>
                              <?php
                              }
                              ?>
                           </div>
                        </div>
                     </div>
                     <script>
                        function showDeleteForm() {
                           var x = document.querySelector('input[name="requestToDelete"]:checked').value;
                           document.getElementById('deleteRequestDiv').innerHTML += '<input id="UUIDselected" type="hidden" name="UUIDselected" value="' + x + '"/>';
                           document.getElementById("deleterequest").style.display = 'none';
                           document.getElementById("mainsubmit").style.display = 'none';
                           document.getElementById("deleteRequestDiv").style.display = 'block';
                        }
                     </script>
                     <div id="deleteRequestDiv" class="card-panel center" style="display: none;">
                        <form action="request.php" method="POST">
                           <p>This action cannot be undone. Are you sure you want to delete your service?</p>
                           <button class="btn waves-effect waves-light" type="submit">I am sure, proceed<i class="material-icons right">delete_forever</i>
                           </button>

                     </div>
                  </form>
               <?php
               }
               ?>

               <button id="mainsubmit" class="btn waves-effect waves-light" style="display:none;" type="submit" name="action">Submit
                  <i class="material-icons right">send</i>
               </button>

            </form>
         </div>
      </div>
   </body>

   </html>
<?php
   $dbconnection->close();
   ob_end_flush();
} else {
   header('Location: index.php');
}
?>