// const checkToken = () => {
//   const token = localStorage.getItem('token');
//   if (token) {
//     // cek valid

//     return token;
//   } else {
//     return "false"
//   }

// };

// login
const form = document.getElementById('form');
form.addEventListener('submit', (e) => {
  e.preventDefault()
  const data = new FormData(form);
  const user = data.get('username');
  const pass = data.get('password');
  if (user == "" || pass == "") {
    alert('User and Pass Require')
  } else {
    const url = "http://127.0.0.1:5000/login/",
      credentials = btoa(`${user}:${pass}`);
    fetch(url, {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: {
          "Authorization": `Basic ${credentials}`
        }
      })
      .then((result) => {
        if (result.status == 401) {
          alert("Please check username or password");
        }
        return result.json();
      })
      .then((response) => {
        const token = response['token']
        let tokens = token.split(".");
        const user = JSON.parse(atob(tokens[1]));
        console.log(user)
        if (user['is_admin'] == true){
          localStorage.setItem('token_admin', response['token']);
          window.location.href = '/admin/dashboard.html';
        }
        else{
          localStorage.setItem('token_user', response['token']);
          window.location.href = 'index.html';
        }

    })
      .catch((error) => {
        alert(error);
      });
  }
})

// document.addEventListener('DOMContentLoaded', () => {
//   const token = checkToken();
//   if (token != 'false') {
//     window.location.href = 'index.html';
//   } else {
//     // getProfile(token);
//     console.log('belum login')
//   }
// });