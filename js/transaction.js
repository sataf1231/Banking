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
    showDeposit = document.getElementById("showDeposit")
    showMoney = document.getElementById("balanceDeposit")
    showDeposit1 = document.getElementById("showDeposit1")
    showMoney1 = document.getElementById("balanceDeposit1")
    showDeposit2 = document.getElementById("showDeposit2")
    showMoney2 = document.getElementById("balanceDeposit2")
    for (i = 0; i < data.length; i++) {
        if (i == 0){
            showDeposit.innerHTML += `<div class="btn-group" role="group"
                                                  aria-label="Basic radio toggle button group">
                                                  <input type="radio" class="btn-check" name="btnradio" id="${data[i].name_account}1" onclick="show_money(`+data[i].balance+`,`+data[i].id+`)"
                                                      autocomplete="off" checked>
                                                  <label class="btn btn-outline-primary" for="${data[i].name_account}1">${data[i].name_account}</label>
                                              </div>`
            showMoney.value =  `${data[i].balance}`
        }
        else{
            showDeposit.innerHTML += `<div class="btn-group" role="group"
                                                  aria-label="Basic radio toggle button group">
                                                  <input type="radio" class="btn-check" name="btnradio" id="${data[i].name_account}1" onclick="show_money(`+data[i].balance+`, `+data[i].id+`)"
                                                      autocomplete="off">
                                                  <label class="btn btn-outline-primary" for="${data[i].name_account}1">${data[i].name_account}</label>
                                              </div>`
        }
        if (i == 0){
          showDeposit1.innerHTML += `<div class="btn-group" role="group"
                                                aria-label="Basic radio toggle button group">
                                                <input type="radio" class="btn-check" name="btnradio" id="${data[i].name_account}2" onclick="show_money1(`+data[i].balance+`,`+data[i].id+`)"
                                                    autocomplete="off" checked>
                                                <label class="btn btn-outline-primary" for="${data[i].name_account}2">${data[i].name_account}</label>
                                            </div>`
          showMoney1.value =  `${data[i].balance}`
      }
      else{
          showDeposit1.innerHTML += `<div class="btn-group" role="group"
                                                aria-label="Basic radio toggle button group">
                                                <input type="radio" class="btn-check" name="btnradio" id="${data[i].name_account}2" onclick="show_money1(`+data[i].balance+`, `+data[i].id+`)"
                                                    autocomplete="off">
                                                <label class="btn btn-outline-primary" for="${data[i].name_account}2">${data[i].name_account}</label>
                                            </div>`
      }
      if (i == 0){
        showDeposit2.innerHTML += `<div class="btn-group" role="group"
                                              aria-label="Basic radio toggle button group">
                                              <input type="radio" class="btn-check" name="btnradio" id="${data[i].name_account}3" onclick="show_money2(`+data[i].balance+`,`+data[i].id+`)"
                                                  autocomplete="off" checked>
                                              <label class="btn btn-outline-primary" for="${data[i].name_account}3">${data[i].name_account}</label>
                                          </div>`
        showMoney2.value =  `${data[i].balance}`
    }
    else{
        showDeposit2.innerHTML += `<div class="btn-group" role="group"
                                              aria-label="Basic radio toggle button group">
                                              <input type="radio" class="btn-check" name="btnradio" id="${data[i].name_account}3" onclick="show_money2(`+data[i].balance+`, `+data[i].id+`)"
                                                  autocomplete="off">
                                              <label class="btn btn-outline-primary" for="${data[i].name_account}3">${data[i].name_account}</label>
                                          </div>`
    }
    }
  })
  .catch((error) => {
    console.error(error);
  });

  function show_money(data,id){
    showMoney.value = data
    // console.log(data,id)
    
    document.getElementById('depositBtn').setAttribute('onclick','depositAccount("'+id+'")')
  }

  function show_money1(data,id){
    showMoney1.value = data
    // console.log(data,id)
    
    document.getElementById('withdrawBtn').setAttribute('onclick','withdrawAccount("'+id+'")')
  }

  function show_money2(data,id){
    showMoney2.value = data
    console.log(data,id)
    
    document.getElementById('transferBtn').setAttribute('onclick','transferAccount("'+id+'")')
  }
  addEventListener('DOMContentLoaded', (event) => {

    // alert("cek")
    $("#depositAmount").replaceWith('<input type="text" class="form-control" placeholder="ex 50000" id="depositAmount">')
    $("#withdrawAmount").replaceWith('<input type="text" class="form-control" placeholder="ex 50000" id="withdrawAmount">')
    $("#transferAmount").replaceWith('<input type="text" class="form-control" placeholder="ex 50000" id="transferAmount">')
    $("#transferId").replaceWith('<input type="text" class="form-control" placeholder="ex 1103160200" id="transferId">')
  });
  // $("#depositAmount").replaceWith('<input type="text" class="form-control" placeholder="ex 50000" id="depositAmount">')
  
  function depositAccount(id){
    const getAmount = document.getElementById("depositAmount").value;
    
    const addSave = { 
      id: parseInt(id),
      amount:parseInt(getAmount)
    };
    // console.log(addSave)
    fetch('http://127.0.0.1:5000/save/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'x-access-token': checkToken(token)
      },
      body: JSON.stringify(addSave)
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      // console.log(data)
      alert('Successfully Deposit', data);
      window.location.reload()
    })
    .catch((error) => {
      console.error(error);
    })
  };

  function withdrawAccount(id){
    const getAmount = document.getElementById("withdrawAmount").value;
    
    const addWithdraw = { 
      id: parseInt(id),
      amount:parseInt(getAmount)
    };
    // console.log(addSave)
    fetch('http://127.0.0.1:5000/withdraw/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'x-access-token': checkToken(token)
      },
      body: JSON.stringify(addWithdraw)
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      // console.log(data)
      alert('Successfully Withdraw', data);
      window.location.reload()
      // getAmount.reset()
    })
    .catch((error) => {
      console.error(error);
    })
  };

  function transferAccount(id){
    const getAmount = document.getElementById("transferAmount").value;
    const getToAccount = document.getElementById("transferId").value;
    console.log(getAmount,getToAccount)
    const addTransfer = { 
      from_account_id: parseInt(id),
      amount:parseInt(getAmount),
      to_account_id:parseInt(getToAccount)
    };
    // console.log(addSave)
    fetch('http://127.0.0.1:5000/transfer/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'x-access-token': checkToken(token)
      },
      body: JSON.stringify(addTransfer)
    })
    .then(response => {
      return response.json()
    })
    .then(data => {
      console.log(data)
      alert('Successfully Transfer', data);
      window.location.reload()
      // getAmount.reset()
    })
    .catch((error) => {
      console.error(error);
    })
  };

  
