$(document).ready(function(){
  function find_targets(piece){
    var orthogonals = [[0,1],[0,-1],[1,0],[-1,0]]
    var diagonals   = [[-1,-1],[-1,+1],[+1,-1],[+1,+1]]
    var strengths = {water:'fire', fire:'plant', plant:'water'}
    
    // Find legal spaces to move to
    var kind   = piece.attr('data_kind')
    var movements = orthogonals
    if(kind == "wizard") movements = orthogonals.concat(diagonals)
    
    var space = piece.parents('.space:first')
    var location = space.attr("data_location").split('-')
    filter = $(movements).map(function(){
      return "[data_location="+(parseInt(location[0])+this[0])+"-"+(parseInt(location[1])+this[1])+"]"
    }).get().join(',')
    var neighbors = $('.space').filter(filter)
    
    // blacklist ones with disagreeable pieces on them
    var level = kind.slice(kind.length-1,kind.length)
    var type  = kind.slice(0, kind.length-1)
    var player = piece.attr('data_player')
    var targets = neighbors.filter(function(){
      var piece = $(this).children('.piece')
      if(!piece.length) return true               // blank spaces are always legal
      if(piece && kind == 'wizard') return false  // wizards can't attack
      var target_player = piece.attr('data_player')
      if(player == target_player) return false    // can't attack yourself
      var target_kind = piece.attr('data_kind')
      var target_level = target_kind.slice(kind.length-1,kind.length)
      var target_type  = target_kind.slice(0, kind.length-1)
      if(strengths[type] == target_type) return true
      if(strengths[target_type] == type) return false
      if(type == target_type && level > target_level) return true // same type fights by level
      return false
    })
    return targets
  }
  
  
  // Moving Pieces
  var dragging = false
  $(".piece").draggable({helper:'clone', scroll:true, start:function(event,ui){
      dragging = true
      $(this).addClass('dragging')
    }, stop:function(event,ui){
      dragging = false
      $('.highlight').removeClass('highlight')
      $(this).removeClass('dragging')
    }
  })
  $(".space").droppable({accept:".piece", drop:function(event,ui){
    piece = ui.draggable
    from = piece.parents(".space:first").attr("data_location")
    to = $(this).attr("data_location")

    // check if it's a legal move before we send it
    if($.inArray(this,find_targets(piece)) == -1) return

    data = {from_space:from, to_space:to}
    $.ajax({type:"POST", url:"/games/"+game_id+"/moves", data:data, success:function(response){
      $('#status').text('')
    }, error:function(response){
      $('#status').text(response.responseText)
    }})
  }})
  
  // hilighting moves
  $(".piece").hover(function(){
    if(!dragging) find_targets($(this)).addClass('highlight')
  }, function(){
    if(!dragging) $('.highlight').removeClass('highlight')
  })
  
    
  // Getting Game Events
  event_period = 1000
  function checkEvents(){
    $.getJSON('/games/'+game_id+'/events/'+timestamp, function(response){
      if(response.timestamp) timestamp = response.timestamp
      if(response.events){
        $.each(response.events ,function(){
          if(this.type == "move"){
            var from_space = $("[data_location="+this.from_space+"]")
            var to_space = $("[data_location="+this.to_space+"]")
            to_space.children(".piece").remove()
            from_space.children(".piece").appendTo(to_space)
            //console.debug(from_space.children(".piece"), to_space.children(".piece"))
            turn += 1
          } else if(this.type == "chat"){
            $('#messages').prepend("<p>"+this.name+": "+this.text+"</p>" )        
          }
        })
      }
      setTimeout(checkEvents, event_period)
    })
  }
  setTimeout(checkEvents, event_period)  

  // Sending Game Chat
  $('#chat').submit(function(event){
    event.preventDefault()
    var field = $('#chat [name=text]')
    if(field.val() == '') return
    data = $(this).serialize()
    field.val('')
    $.post('/games/'+game_id+'/chat',data)    
  })
})
