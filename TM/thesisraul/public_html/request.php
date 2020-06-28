<?php
session_start();
ob_start();

// Debug errors
#ini_set("display_errors",1);
#error_reporting(E_ALL);

if (isset($_POST['servicesize']) or isset($_POST['UUIDselected'])) {

  include("../conf/settings.php");
  $dbconnection = mysqli_connect($host, $username, $password, $db_name);
  unset($host, $username, $password, $db_name);

  if (!$dbconnection) {
    die("CONNECTION FAILED: " . $dbconnection->mysqli_connect_error());
  }

  # Function code taken from https://www.php.net/manual/en/function.uniqid.php
  function gen_request_uuid()
  {
    return sprintf(
      '%04x%04x%04x%04x%04x%04x%04x%04x',
      //32 bits for "time_low"
      mt_rand(0, 0xffff),
      mt_rand(0, 0xffff),

      // 16 bits for "time_mid"
      mt_rand(0, 0xffff),

      // 16 bits for "time_hi_and_version",
      // four most significant bits holds version number 4
      mt_rand(0, 0x0fff) | 0x4000,

      // 16 bits, 8 bits for "clk_seq_hi_res",
      // 8 bits for "clk_seq_low",
      // two most significant bits holds zero and one for variant DCE1.1
      mt_rand(0, 0x3fff) | 0x8000,

      // 48 bits for "node"
      mt_rand(0, 0xffff),
      mt_rand(0, 0xffff),
      mt_rand(0, 0xffff)
    );
  }

  // Operation mode array iteration
  $sessionOperationMode = $_SESSION['mode'];
  $nameIDdb = $_SESSION['name-id'];
  $gen_timestamp_date = date('d-m-Y H:i:s');
  $emaildb = $_SESSION['email'];
  $homedb = $_SESSION['home'];
  $departmentdb = $_SESSION['department'];
  $roledb = $_SESSION['role'];
  $firstName = $_SESSION['firstName'];
  $surname = $_SESSION['surname'];

  if ($sessionOperationMode == "create" || $sessionOperationMode == "modify") {

    global $operationmode;
    $operationmode = array();
    if ($_POST['spec'] == "defined") {
      $times = array("start_date" => $_POST['start-date'], "duration" => $_POST['duration']);
      $spec = array("defined" => $times);
      $operationmode = array($sessionOperationMode => $spec);
      # For database
      $operationModes = $sessionOperationMode;
      $createMode = "defined";
      $startDate = $_POST['start-date'];
      $timeDuration = $_POST['duration'];
    } else {
      $spec = array("undefined" => "true");
      $timeDuration = 0;
      $operationmode = array($sessionOperationMode => $spec);
      $operationModes =  $sessionOperationMode;
      $createMode = "undefined";
    }

    // Users array iteration
    $usersArray = array();
    $numberstudents = $_POST['numberstudents'];
    for ($i = 1; $i <= $numberstudents; $i++) {
      $usersArray["user$i"] = $_POST["user$i"];
    }

    // User cooperation mode array iteration
    $usersCoop = array();
    $postCoopMode = $_POST['coopmode'];
    if ($postCoopMode == "groups") {
      $groupsArray = array();
      $numbergroups = $_POST['numgroupsrange'];
      for ($i = 1; $i <= $numbergroups; $i++) {
        $groupsArray["group$i"] = $_POST["group$i"];
      }
      $usersCoop["groups"] = $groupsArray;
      # For database
      $userCooperationModeDB = "groups";
    } else {
      $numbergroups = 0;
      $usersCoop = array($postCoopMode => "true");
      $userCooperationModeDB = $postCoopMode;
    }

    # Variables
    $UUID = gen_request_uuid();
    if ($sessionOperationMode == "modify") {
      $UUID = $_POST['UUIDselected'];
    }
    $serviceSizedb = $_POST['servicesize'];
    $lessonTypedb = $_POST['lessontype'];
    $lessonTopicdb = $_POST['lessontopic'];
    $homeDirectoriesdb = $_POST['homedirectories'];
    $additionalServicesyml = $_POST["additionalservices"];
    $whatPersistedItemsyml = $_POST["WhatPersistedItems"];

    $additionalServicesdb = "";
    $whatPersistedItemsdb = "";
    foreach ($additionalServicesyml as $item) {
      $additionalServicesdb .= $item;
    }

    foreach ($whatPersistedItemsyml as $item) {
      $whatPersistedItemsdb .= $item;
    }
    /*
    foreach($usersArray as $item) {
        var_dump($item);
    } 

    foreach($groupsArray as $item) {
        var_dump($item);
    }
    */

    // Main teacher model array
    $main = array(
      "requestor_id" => $nameIDdb,
      "timestamp_start" => $gen_timestamp_date,
      "firstname" => $firstName,
      "surname" => $surname,
      "request_UUID" => $UUID,
      "requestor_email" => $emaildb,
      "home_institute" => $homedb,
      "home_department" => $departmentdb,
      "teacher_role" => $roledb,
      "operation_mode" => $operationmode,
      "machine_size" => $serviceSizedb,
      "lesson_type" => $lessonTypedb,
      "lesson_topic" => $lessonTopicdb,
      "home_directories" => $homeDirectoriesdb,
      "users" => $usersArray,
      "user_cooperation_mode" => $usersCoop,
      "additional_services" => array($additionalServicesyml => "true"),
      "persisted_items" => array("what" => $whatPersistedItemsyml)
    );

    # Create / modify TM request file
    $TM_output = "$webPath/requests/TMrequest-$UUID.yaml";
    $myfile = fopen($TM_output, "w") or die("Unable to open file!");
    $txt = yaml_emit($main);
    fwrite($myfile, $txt);
    fclose($myfile);

    if ($sessionOperationMode == "create") {
      # Insert values into database registries
      $sqlinsert = "INSERT INTO tmrequests(id, tstart, uuid, fname, sname, email, homeinst, homedept, trole, opmode, cmode, startd, span) VALUES ('$nameIDdb', '$gen_timestamp_date', '$UUID', '$firstName', '$surname', '$emaildb', '$homedb', '$departmentdb', '$roledb', '$operationModes', '$createMode', '$startDate', '$timeDuration');";
      $sqlinsert2 = "INSERT INTO tmspecs(id, msize, ltype, ltopic, homedir, nusers, coopmode, ngroups, addsrv, whatpi) VALUES ('$UUID', '$serviceSizedb', '$lessonTypedb', '$lessonTopicdb', '$homeDirectoriesdb', '$numberstudents', '$userCooperationModeDB', '$numbergroups', '$additionalServicesdb', '$whatPersistedItemsdb');";

      if (!mysqli_query($dbconnection, $sqlinsert)) {
        echo "Error: " . $sqlinsert . "<br>" . mysqli_error($dbconnection);
      }
      if (!mysqli_query($dbconnection, $sqlinsert2)) {
        echo "Error: " . $sqlinsert2 . "<br>" . mysqli_error($dbconnection);
      }
      $message = "Your request form has been sent! Your request has been registered with identifier $UUID, save it for future actions on the service. Before long you will receive an email with the status of your request.";
    } elseif ($sessionOperationMode == "modify") {
      $sqlupdate = "UPDATE tmrequests SET tstart='$gen_timestamp_date', fname='$firstName', sname='$surname', email='$emaildb', homeinst='$homedb', homedept='$departmentdb', trole='$roledb', opmode='$operationModes', cmode='$createMode', startd='$startDate', span='$timeDuration' WHERE uuid='$UUID';";

      $sqlupdate2 = "UPDATE tmspecs SET msize='$serviceSizedb', ltype='$lessonTypedb', ltopic='$lessonTopicdb', homedir='$homeDirectoriesdb', nusers='$numberstudents', coopmode='$userCooperationModeDB', ngroups='$numbergroups', addsrv='$additionalServicesdb', whatpi='$whatPersistedItemsdb' WHERE id='$UUID';";
      if (!mysqli_query($dbconnection, $sqlupdate)) {
        echo "Error: " . $sqlupdate . "<br>" . mysqli_error($dbconnection);
      }
      if (!mysqli_query($dbconnection, $sqlupdate2)) {
        echo "Error: " . $sqlupdate2 . "<br>" . mysqli_error($dbconnection);
      }
      $message = "Your modification request form has been sent! The request that is going to be modified is $UUID. Before long you will receive an email with the status of your request.";
    }
  } elseif ($sessionOperationMode == "delete") {
    $UUID = $_POST['UUIDselected'];

    # Delete TM request file
    # Updateexistent file

    $TM_output = "$webPath/requests/TMrequest-$UUID.yaml";
    $TM_contents = file_get_contents($TM_output);
    $TM_contents = str_replace("create","delete",$TM_contents);
    file_put_contents($TM_output,$TM_contents);

    $TM_contents = file_get_contents($TM_output);
    $TM_contents = str_replace("modify","delete",$TM_contents);
    file_put_contents($TM_output,$TM_contents);

    $sqldelete = "UPDATE tmrequests SET opmode='$sessionOperationMode' WHERE uuid='$UUID';";

    if (!mysqli_query($dbconnection, $sqldelete)) {
      echo "Error: " . $sqldelete . "<br>" . mysqli_error($dbconnection);
    }
    $message = "Your deletion request form has been sent! Your service with identifier $UUID is going to be deleted from MCHE systems. Before long you will receive an email with the status of your request.";
  }

  # Execute bash script in $webPath
  # This executes the main Python orchestrator code and passes UUID as first argument
  # Debug:
  # echo shell_exec("whoami");
  $cmd = 'nohup sudo ' . $webPath . '/bash_call.sh ' . $UUID . ' >/dev/null 2>&1';
  exec($cmd);

  # HTML Pie Data
  # Gather data for different Lesson Types and display it
  $query1  = "SELECT * FROM tmspecs WHERE ltype = 'it';";
  $result1 = mysqli_query($dbconnection, $query1) or die(mysqli_error('Query error'));
  $row1 = mysqli_num_rows($result1);

  $query2  = "SELECT * FROM tmspecs WHERE ltype = 'biology';";
  $result2 = mysqli_query($dbconnection, $query2) or die(mysqli_error('Query error'));
  $row2 = mysqli_num_rows($result2);

  $query3  = "SELECT * FROM tmspecs WHERE ltype = 'maths';";
  $result3 = mysqli_query($dbconnection, $query3) or die(mysqli_error('Query error'));
  $row3 = mysqli_num_rows($result3);

  $query4  = "SELECT * FROM tmspecs WHERE ltype = 'physics';";
  $result4 = mysqli_query($dbconnection, $query4) or die(mysqli_error('Query error'));
  $row4 = mysqli_num_rows($result4);
?>

  <!DOCTYPE html>
  <html>

  <head>
    <title>MEC Teacher request</title>
    <meta name="viewport" content="width = device-width, initial-scale = 1">
    <link rel="shortcut icon" type="image/x-icon" href="img/mche.ico" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
    <style>
      @import url('https://fonts.googleapis.com/css?family=Poppins:600&display=swap');

      * {
        margin: 0;
        padding: 0;
      }

      body {
        min-height: 100vh;
        text-align: center;
      }
    </style>
  </head>

  <body class="container">
    <div class="col s12 m12 l6">
      <div class="card-panel">
        <!-- Nav and info-->
        <nav class="navbar-fixed">
          <div class="nav-wrapper">
            <h3>Teacher request</h3>
          </div>
        </nav>
        <div class="col s12 m7">
          <div class="card horizontal hoverable">
            <div class="card-stacked">
              <div class="card-content">
                <p><?php echo $message; ?></p>
              </div>
            </div>
          </div>
        </div>
        <h5>Statistics about most requested types of lessons</h5>
        <canvas id="lessonsChart" style="width: 500px!important"></canvas>
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@2.9.3/dist/Chart.min.js"></script>
    <script type="text/javascript">
      $(document).ready(function() {
        const chart = document.getElementById('lessonsChart').getContext('2d');
        let myChart = new Chart(chart, {
          type: 'pie',
          data: {
            labels: ['IT', 'Biology', 'Maths', 'Physics'],
            datasets: [{
              label: '# of Requests',
              data: [<?php echo $row1; ?>, <?php echo $row2; ?>, <?php echo $row3; ?>, <?php echo $row4; ?>],
              backgroundColor: ['#E4572E', '#17BEBB', '#FFC914', '#00FF00'],
              borderWidth: 1
            }]
          }
        });
      });
    </script>
  </body>

  </html>
<?php
  $dbconnection->close();
  ob_end_flush();
} else {
  header('Location: index.php');
}
?>