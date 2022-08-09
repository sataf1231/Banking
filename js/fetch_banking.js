const checkToken = () => {
  const token = localStorage.getItem('token_user');
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
    getProfile(token);
  }
});

//logout
function logout() {
  localStorage.removeItem('token_user');
  window.location.href = 'login.html';
}

const getProfile = (token) => {
  // get profile dari backend menggunakan token
  // console.log(token) 
  let tokens = token.split(".");
  const user = JSON.parse(atob(tokens[1]));
  document.getElementById('name_user').innerText = user['name_user'];
  document.getElementById('getName').innerText = user['name_user'];
  // console.log(user)
};


document.addEventListener('DOMContentLoaded', () => {
  const token = checkToken();
  if (token == 'false') {
    window.location.href = 'login.html';
  } else {
    getProfile(token);
  }
});

//get token
const token = checkToken();
let tokens = token.split(".");
const public_id = JSON.parse(atob(tokens[1]));


fetch('http://127.0.0.1:5000/account_id/', {
    method: 'GET',
    credentials: 'include',
    headers: {
      'x-access-token': checkToken(token)
    }
  })
  .then(response => {
    return response.json()
  })
  .then(data => {
    // console.log(data)
    overview = document.getElementById("overview")
    for (i = 0; i < data.length; i++) {
      overview.innerHTML +=
        `<div class="list-item">
      <div class="list-item-company">
          <figure class="list-item-company-logo">
              <img src="assets/logo/bank-front.png" />
          </figure>
          <div class="list-item-company-info">
              <h6 class="list-item-company-name">` + data[i].name_account + `</h6>
              <a>` + data[i].id + `</a>
          </div>
      </div>
      <div class="list-item-transaction">
          <div class="list-item-transaction-values">
              <span class="list-item-transaction-value list-item-transaction-value--positive">
              Rp.` + data[i].balance + `
              </span>
          </div>
          <button class="list-item-transaction-action">
              <a href="transaction.html"><img src="assets/logo/option-trans.png" /></a>

          </button>
      </div>
  </div>`
    }
  })
  .catch((error) => {
    console.error(error);
  });


fetch('http://127.0.0.1:5000/history/', {
    method: 'GET',
    credentials: 'include',
    headers: {
      'x-access-token': checkToken(token)
    }
  })
  .then(response => {
    return response.json()
  })
  .then(data => {
    const grouped = data.reduce((acc, item )=>{
      if(acc[item.transaction_date]){
        acc[item.transaction_date].push(item);
      }else{
        acc[item.transaction_date] = [item];
      }
      return acc;
    },{})
    let array = Object.keys(grouped)
    l =[]
    overview_body = document.getElementById("overview-history")
      // for(let i = 0; i< grouped.length; i++){
        console.log(grouped)
        for(let i = 0; i< array.length; i++){
          // console.log(grouped[array[i]])
          l.push(grouped[array[i]])
          overview_body.innerHTML += `<div class="history d-block" id=`+ array[i] +`><h5> `+array[i] + `</h5> </div>`
          // for(let j = 0; i< grouped[array[i]].length; j++){
          //   console.log(grouped[array[i]][j])
        }
        // for(let j = 0; j< l.length; j++){
        //   console.log(l[j][0])
        // }
        fungsi2(l,array)
        console.log(l[1][0].desc)
        
  })
  .catch((error) => {
    console.error(error);
  });
function fungsi2(l,arr){
// console.log(l)
  for(let j = 0; j< l.length; j++){
    overview_body2 = document.getElementById(arr[j])
    for(let k = 0; k< l[j].length; k++){
      // console.log(l[j][k])
      if (l[j][k].desc == 'Save'){
        overview_body2.innerHTML +=
          `<div class="list-item">
              <div class="list-item-company">
                  <figure class="list-item-company-logo" >
                    <img src="assets/logo/deposit.png"/>
                  </figure>
                  <div class="list-item-company-info">
                      <h6 class="list-item-company-name">` + l[j][k].from_account_id + `</h6>
                      <p class="list-item-company-hashtag">`+l[j][k].desc+` </p>
                  </div>
              </div>
              <div class="list-item-transaction">
                  <div class="list-item-transaction-values">
                      <span class="list-item-transaction-value list-item-transaction-value--positive"  style="color: green;">+Rp.` +l[j][k].amount+ `
                      </span>
                      <time class="list-item-transaction-time" ></time>
                  </div>
                  <button class="list-item-transaction-action">
                      <i class="ph-caret-down-bold"></i>
                  </button>
              </div>
          </div>`
      }
      else if (l[j][k].desc == 'Withdraw'){
        overview_body2.innerHTML +=
          `<div class="list-item">
              <div class="list-item-company">
                  <figure class="list-item-company-logo" >
                    <img src="assets/logo/withdraw.png"/>
                  </figure>
                  <div class="list-item-company-info">
                      <h6 class="list-item-company-name">` + l[j][k].from_account_id + `</h6>
                      <p class="list-item-company-hashtag">`+l[j][k].desc+` </p>
                  </div>
              </div>
              <div class="list-item-transaction">
                  <div class="list-item-transaction-values">
                      <span class="list-item-transaction-value list-item-transaction-value--positive" style="color: red;">-Rp.` +l[j][k].amount+ `
                      </span>
                      <time class="list-item-transaction-time" ></time>
                  </div>
                  <button class="list-item-transaction-action">
                      <i class="ph-caret-down-bold"></i>
                  </button>
              </div>
          </div>`
      }
      else{
        overview_body2.innerHTML +=
          `<div class="list-item">
              <div class="list-item-company">
                  <figure class="list-item-company-logo" >
                    <img src="assets/logo/transfer.png"/>
                  </figure>
                  <div class="list-item-company-info">
                      <h6 class="list-item-company-name">` + l[j][k].to_account_id + `</h6>
                      <p class="list-item-company-hashtag">`+l[j][k].desc+` </p>
                  </div>
              </div>
              <div class="list-item-transaction">
                  <div class="list-item-transaction-values">
                      <span class="list-item-transaction-value list-item-transaction-value--positive"  style="color: red;">-Rp.` +l[j][k].amount+ `
                      </span>
                      <time class="list-item-transaction-time" >From ` + l[j][k].from_account_id + `</time>
                  </div>
                  <button class="list-item-transaction-action">
                      <i class="ph-caret-down-bold"></i>
                  </button>
              </div>
          </div>`
      }
  }
}
}
  function showModal(){
    $('#modalPass').modal('show');
  };
  function changePass(){
    const getPassword = document.getElementById("modalPassword").value;
    const updateUser = {
      password:getPassword
    }
    console.log(getPassword)
    fetch('http://127.0.0.1:5000/user_password/', {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'x-access-token': checkToken(token),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateUser)
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      console.log(data)
      alert('Successfully Update Password', data);
      window.location.reload()
    })
    .catch((error) => {
      console.error(error);
    })
  };
  
