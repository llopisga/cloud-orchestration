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
               <h3>Teacher request</h3>
            </div>
         </nav>
         <div class="col s12 m7">
            <div class="card horizontal hoverable">
               <div class="card-stacked">
                  <div class="card-content">
                     <p>Welcome to the application form to request on-demand educational services for high school students in MCHE cloud. It is designed to facilitate the application process, in case you have doubts about any option, you can mouse over it for a brief description.</p>
                  </div>
               </div>
            </div>
         </div>

         <!-- Request form-->
         <form class="col s12 m12 l6" action="operation_mode.php" method="POST" id="request-form">
            <div class="card-panel">

               <!-- Teacher Information-->
               <input value="Teacher Information" type="text" disabled />
               <div class="row">
                  <div class="input-field col s6" title="Your teacher identificator">
                     <i class="material-icons prefix">verified_user</i>
                     <label for="name-id">Requestor ID</label>
                     <input required id="name-id" name="name-id" type="text" class="active validate" />
                  </div>
                  <div class="input-field col s6" title="Your email for reciving notifications">
                     <i class="material-icons prefix">email</i>
                     <label for="email">Email</label>
                     <input required id="email" name="email" type="email" class="validate">
                  </div>
               </div>
               <div class="row">
                  <div class="input-field col s6" title="Your first name">
                     <i class="material-icons prefix">account_circle</i>
                     <label for="firstName">First Name</label>
                     <input required id="firstName" name="firstName" type="text" class="active validate" />
                  </div>
                  <div class="input-field col s6" title="Your surname">
                     <i class="material-icons prefix">account_circle</i>
                     <label for="surname">Surname</label>
                     <input required id="surname" name="surname" type="text" class="validate">
                  </div>
               </div>
               <div class="row">
                  <div class="input-field col s6" title="Input the acronym. E.g. AGH">
                     <i class="material-icons prefix">home</i>
                     <label for="home">Home Institution</label>
                     <input required id="home" name="home" type="text" class="validate" />
                  </div>
                  <div class="input-field col s6" title="Input the acronym">
                     <i class="material-icons prefix">label</i>
                     <label for="department">Home Department</label>
                     <input required id="department" name="department" type="text" class="validate" />
                  </div>
               </div>
               <div class="row">
                  <div class="input-field col s6" title="Your role for requesting the service">
                     <h6><i class="material-icons left">school</i>Teacher Role</h6>
                     <p><label>
                           <input checked class="actionmode" name="role" id="leadingTeacher" type="radio" value="ldteacher" />
                           <span>Leading Teacher</span>
                        </label></p>
                     <p><label>
                           <input class="actionmode" name="role" id="teacher" type="radio" value="teacher" />
                           <span>Secondary School Teacher</span>
                        </label></p>
                  </div>
               </div>
            </div>

            <!-- Operation mode -->
            <div class="card-panel center">
               <input value="Operation Mode" type="text" disabled />
               <div class="row">
                  <div class="input-field col s12">
                     <h6>Which action do you want to perform?</h6>
                     <p><label>
                           <input checked onclick="createRequestdiv()" class="actionmode" name="mode" id="create" type="radio" value="create" />
                           <span>Create</span>
                        </label></p>
                     <p><label>
                           <input onclick="modifyRequestdiv()" class="actionmode" name="mode" id="modify" type="radio" value="modify" />
                           <span>Modify</span>
                        </label></p>
                     <p><label>
                           <input onclick="deleteRequestdiv()" class="actionmode" name="mode" id="delete" type="radio" value="delete" />
                           <span>Delete</span>
                        </label></p>
                  </div>
               </div>
            </div>


            <button class="btn waves-effect waves-light" type="submit" name="action">Submit
               <i class="material-icons right">send</i>
            </button>
         </form>
      </div>
   </div>
</body>

</html>