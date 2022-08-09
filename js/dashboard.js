/* globals Chart:false, feather:false */
(function () {
  'use strict'

  feather.replace({ 'aria-hidden': 'true' })

})()

const checkToken = () => {
  const token = localStorage.getItem('token_admin');
  if (token) {
    return token;
  } else {
    return window.location.href = '../login.html';
  }

};

document.addEventListener('DOMContentLoaded', () => {
  const token = checkToken();
  if (!token) {
    window.location.href = '../login.html';
  } else {
    console.log(token)
  }
});

function logout() {
  localStorage.removeItem('token_admin');
  window.location.reload()
}

// const getProfile = (token) => {
//   // get profile dari backend menggunakan token
//   // console.log(token) 
//   let tokens = token.split(".");
//   const user = JSON.parse(atob(tokens[1]));
//   // document.getElementById('name_user').innerText = user['name_user'];
//   console.log(user)
//   return user
// };


fetch('http://127.0.0.1:5000/branch/', {
    method: 'GET',
    credentials: 'include',
    // headers: {
    //   'x-access-token': checkToken(token)
    // }
  })
  .then(response => {
    return response.json()
  })
  .then(json => {
    // console.log(json)
    const tableBranch = $('#tableBranch').DataTable({
      data: json,
      columns:[
        {
          data:'id'
        },
        {
          data:'name_branch'
        },
        {
          data:'city'
        },
      ]
    });
    $('#tableBranch tbody').on('click', 'tr', function () {
      let data = tableBranch.row(this).data();
      // console.log(data['id'])
      $('#modalBranch').modal('show');
      document.getElementById('modalBranchname').value = data['name_branch']
      document.getElementById('modalCity').value = data['city']
      document.getElementById('btn-update-branch').setAttribute('onclick','updateThisBranch("'+data['id']+'","'+data['name_branch']+'","'+data['city']+'")')
    });
  })
  .catch((error) => {
    console.error(error);
  });

  function updateThisBranch(id,name_branch,city){
    // console.log(id,name_branch,city)
    const getBranchname = document.getElementById('modalBranchname')
    const getCity = document.getElementById('modalCity')
  
    name_branch = getBranchname.value
    city = getCity.value
  
    const updateBranch={
      name_branch:name_branch,
      city:city
    };
    console.log(updateBranch)
    fetch('http://127.0.0.1:5000/branch/'+id+'/', {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'x-access-token': checkToken()
      },
      body: JSON.stringify(updateBranch)
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      console.log(data)
      alert('Successfully Update Status', data);
      window.location.reload()
    })
    .catch((error) => {
      console.error(error);
    })
  };

  function createBranch(){
    const getBranchname = document.getElementById("branchName").value;
    const getBranchcity = document.getElementById("branchCity").value;
  
    const addBranch = { 
      name_branch: getBranchname,
      city: getBranchcity
    };
    console.log(addBranch)
    fetch('http://127.0.0.1:5000/create_branch/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'x-access-token': checkToken()
      },
      body: JSON.stringify(addBranch)
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      console.log(data)
      alert('Successfully Create Branch', data);
      window.location.reload()
    })
    .catch((error) => {
      console.error(error);
    })
  };

  function createDate(){
    const getStartdate = document.getElementById("startDate").value;
    const getEnddate = document.getElementById("endDate").value;
  
    const addDate = { 
      start_date: getStartdate,
      end_date: getEnddate
    };
    // console.log(addDate)
    fetch('http://127.0.0.1:5000/branch-report-transaction/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'x-access-token': checkToken()
      },
      body: JSON.stringify(addDate)
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      console.log(data)
      // alert('Successfully Create Branch', data);
      // window.location.reload()
    })
    .catch((error) => {
      console.error(error);
    })
  };

  fetch('http://127.0.0.1:5000/branch-report-transaction-get/', {
    method: 'GET',
    credentials: 'include',
    headers: {
      'x-access-token': checkToken()
    }
  })
  .then(response => {
    return response.json()
  })
  .then(json => {
    // console.log(json)
    const tableBranchReport = $('#tableBranchReport').DataTable({
      data: json,
      columns:[
        {
          data:'branch_name'
        },
        {
          data:'total_credit'
        },
        {
          data:'total_debit'
        },
      ]
    });
  })
  .catch((error) => {
    console.error(error);
  });


  fetch('http://127.0.0.1:5000/branch-all-report-total/', {
    method: 'GET',
    credentials: 'include',
    headers: {
      'x-access-token': checkToken()
    }
  })
  .then(response => {
    return response.json()
  })
  .then(data => {
    // console.log(data)
    const getTotaluser = document.getElementById('totalUser')
    const getTotalaccount = document.getElementById('totalAccount')
    const getTotalbalance = document.getElementById('totalBalance')
    for (i = 0; i < data.length; i++){
      getTotaluser.innerHTML =  `${data[i].total_user}`
      getTotalaccount.innerHTML =  `${data[i].total_account}`
      getTotalbalance.innerHTML =  `Rp. ${data[i].total_balance}`
    }

  })
  .catch((error) => {
    console.error(error);
  });

//Page User
//Get user for table
fetch('http://127.0.0.1:5000/user/', {
  method: 'GET',
  credentials: 'include',
  // headers: {
  //   'x-access-token': checkToken(token)
  // }
})
.then(response => {
  return response.json()
})
.then(json => {
  // console.log(json)
  const table = $('#showUser').DataTable({
    data: json,
    columns:[
      {
        data:'id'
      },
      {
        data:'name_user'
      },
      {
        data:'username'
      },
      {
        data:'password'
      },
      {
        data:'phone'
      },
      {
        data:'email'
      },
      {
        data:'address'
      },
    ]
  });
  $('#showUser tbody').on('click', 'tr', function () {
    let data = table.row(this).data();
    // console.log(data['id'])
    $('#modalUser').modal('show');
    document.getElementById('modalFullname').value = data['name_user']
    document.getElementById('modalPhone').value = data['phone']
    document.getElementById('modalEmail').value = data['email']
    document.getElementById('modalAddress').value = data['address']
    document.getElementById('btn-update-user').setAttribute('onclick','updateThisUser("'+data['id']+'","'+data['name_user']+'","'+data['phone']+'","'+data['email']+'","'+data['address']+'")')
  });
})
.catch((error) => {
  console.error(error);
});

function updateThisUser(id,name_user,phone,email,address){
  // console.log(id,name_user,phone,email,address)
  const getFullname = document.getElementById('modalFullname')
  const getPhone = document.getElementById('modalPhone')
  const getEmail = document.getElementById('modalEmail')
  const getAddress = document.getElementById('modalAddress')

  name_user = getFullname.value
  phone = getPhone.value
  email = getEmail.value
  address = getAddress.value

  const updateUser={
    name_user:name_user,
    phone:phone,
    email:email,
    address:address
  };
  console.log(updateUser)
  fetch('http://127.0.0.1:5000/user_update/'+id+'/', {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'x-access-token': checkToken()
    },
    body: JSON.stringify(updateUser)
  })
  .then(response => {
    return response.json()
  })
  .then(data => {
    console.log(data)
    alert('Successfully Update Status', data);
    window.location.reload()
  })
  .catch((error) => {
    console.error(error);
  })
}

// Create User
function createUser(){
  const getFullname = document.getElementById("textFullname").value;
  const getPhone = document.getElementById("textPhone").value;
  const getUsername = document.getElementById("textUsername").value;
  const getPassword = document.getElementById("textPassword").value;
  const getAddress = document.getElementById("textAddress").value;
  const getEmail = document.getElementById("textEmail").value;
  
  const addUser = { 
    name_user: getFullname,
    phone:getPhone,
    username:getUsername,
    password:getPassword,
    address:getAddress,
    email:getEmail
  };
  // console.log(addUser)
  fetch('http://127.0.0.1:5000/user/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'x-access-token': checkToken()
    },
    body: JSON.stringify(addUser)
  })
  .then(response => {
    return response.json()
  })
  .then(data => {
    console.log(data)
    alert('Successfully Create User', data);
    window.location.reload()
  })
  .catch((error) => {
    console.error(error);
  })
};

//Page Account
//Get account for table
fetch('http://127.0.0.1:5000/account/', {
  method: 'GET',
  credentials: 'include',
  // headers: {
  //   'x-access-token': checkToken(token)
  // }
})
.then(response => {
  return response.json()
})
.then(json => {
  // console.log(json)
  $('#showAccount').DataTable({
    data: json,
    columns:[
      {
        data:'id'
      },
      {
        data:'user_name'
      },
      {
        data:'name_account'
      },
      {
        data:'branch_name'
      },
      {
        data:'balance'
      },
      {
        data:'status'
      },
      {data: 'id',
          "render": function ( data ) { 
            return '<button data-edit-account="'+data+'" onclick="changeStatus(event)" class="btn btn-xs btn-dark me-1">Status</button>'
          }
        }
    ]
  });
})
.catch((error) => {
  console.error(error);
});

// Get Dormant Table
fetch('http://127.0.0.1:5000/report-dormant/', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'x-access-token': checkToken()
  }
})
.then(response => {
  return response.json()
})
.then(json => {
  // console.log(json)
  $('#showDormant').DataTable({
    data: json,
    columns:[
      {
        data:'account_name'
      },
      {
        data:'account_number'
      },
      {
        data:'dormant_duration_by_days'
      }
    ]
  });
})
.catch((error) => {
  console.error(error);
});

// Get Dormant Dashboard
fetch('http://127.0.0.1:5000/report-dormant/', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'x-access-token': checkToken()
  }
})
.then(response => {
  return response.json()
})
.then(json => {
  // console.log(json)
  const getTotaldormant = document.getElementById('totalDormant')
  getTotaldormant.innerHTML = json.length
})
.catch((error) => {
  console.error(error);
});

//Get dropdown branch for page account
fetch('http://127.0.0.1:5000/branch/', {
  method: 'GET',
  credentials: 'include', 
})
.then(response => {
    return response.json()
}) 
.then(data => {
    // console.log(data)
    showBranch = document.getElementById('branchState')
    for (i = 0; i < data.length; i++) {
    showBranch.innerHTML += `<option>${data[i].name_branch}</option>`
    }
})
.catch((error) => {
  console.error(error);
});

// Create Account
function createAccount(){
  const getAccname = document.getElementById("accName").value;
  const getUsername = document.getElementById("forUsername").value;
  const getBranch = document.getElementById("branchState").value;

  const addAccount = { 
    name_account: getAccname,
    username: getUsername,
    name_branch:getBranch
  };
  // console.log(addAccount)
  fetch('http://127.0.0.1:5000/account/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'x-access-token': checkToken()
    },
    body: JSON.stringify(addAccount)
  })
  .then(response => {
    return response.json()
  })
  .then(data => {
    console.log(data)
    alert('Successfully Create Account', data);
    window.location.reload()
  })
  .catch((error) => {
    console.error(error);
  })
};

// Change status account
function changeStatus(e){
  console.log(e.target.getAttribute('data-edit-account'))

  fetch('http://127.0.0.1:5000/account/'+e.target.getAttribute('data-edit-account')+'/', {
    method: 'PUT',
    credentials: 'include',
    headers: {
      'x-access-token': checkToken()
    },
  })
  .then(response => {
    return response.json()
  })
  .then(data => {
    console.log(data)
    alert('Successfully Update Status', data);
    window.location.reload()
  })
  .catch((error) => {
    console.error(error);
  })
};

