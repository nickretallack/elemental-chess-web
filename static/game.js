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
      var target_level = target_kind.slice(target_kind.length-1,target_kind.length)
      var target_type  = target_kind.slice(0, target_kind.length-1)
      if(strengths[type] == target_type) return true
      if(strengths[target_type] == type) return false
      if(type == target_type && level > target_level) return true // same type fights by level
      return false
    })
    return targets
  }
  
  
  // Moving Pieces
  var dragging = false
  var sent_events = {}
  function update_dragging(){
    $(".piece").draggable("destroy")

    var player = turn_order[turn % turn_order.length]
    if($.inArray(player,your_players) == -1) return         // no dragging other people's stuff
    
    $(".piece."+player+"-player").draggable({helper:'clone', scroll:true, start:function(event,ui){
        dragging = true
        $(this).addClass('dragging')
      }, stop:function(event,ui){
        dragging = false
        $('.highlight').removeClass('highlight')
        $(this).removeClass('dragging')
      }
    })
  }
  update_dragging()
  $(".space").droppable({accept:".piece", drop:function(event,ui){
    piece = ui.draggable
    from_space = piece.parents(".space:first")
    to_space = $(this)

    // check if it's a legal move before we send it
    if($.inArray(this,find_targets(piece)) == -1) return

    from_space_tag = from_space.attr("data_location")
    to_space_tag = to_space.attr("data_location")
    data = {from_space:from_space_tag, to_space:to_space_tag}
    $.ajax({type:"POST", url:"/games/"+game_id+"/moves", data:data, success:function(response){
      $('#status').text('')
      sent_events[response] = true
      move_message("You move", piece.attr('data_kind'), from_space_tag, to_space_tag)
    }, error:function(response){
      $('#status').text(response.responseText)
    }})
    
    // since we want to be responsive, lets just move the thing right now.
    to_space.children(".piece").remove()
    from_space.children(".piece").appendTo(to_space)
    
    // and advance the turn ourselves
    turn += 1
    update_dragging()
  }})
  
  // hilighting moves
  $(".piece").hover(function(){
    var player = turn_order[turn % turn_order.length]
    if($.inArray(player,your_players) == -1) return         // no dragging other people's stuff
    if($(this).attr('data_player') != player) return

    if(!dragging) find_targets($(this)).addClass('highlight')
  }, function(){
    if(!dragging) $('.highlight').removeClass('highlight')
  })
  
    
  // Getting Game Events
  var min_event_period = 1000
  var event_period = min_event_period
  var event_check_timer
  var last_interaction = new Date().getTime()
  
  function move_message(user, piece, from, to){
    $('#messages').prepend("<p>"+user+" "+piece+" from "+from+" to "+to+"</p>")
  }
  
  function checkEvents(){
    var miliseconds_idle = new Date().getTime() - last_interaction
    event_period = min_event_period + miliseconds_idle*miliseconds_idle / 1000000.0
    
    $.getJSON('/games/'+game_id+'/events/'+timestamp, function(response){
      if(response.timestamp) timestamp = response.timestamp
      if(response.events){
        $.each(response.events ,function(){
          if(sent_events[this.timestamp]){
            // don't apply events you sent yourself
            delete sent_events[this.timestamp]
          } else if(this.type == "move"){
            var from_space = $("[data_location="+this.from_space+"]")
            var to_space = $("[data_location="+this.to_space+"]")
            var piece = from_space.children(".piece")
            to_space.children(".piece").remove()
            piece.prependTo(to_space)
            turn += 1
            update_dragging()
            move_message(this.name+" moves", piece.attr('data_kind'), this.from_space, this.to_space)
          } else if(this.type == "chat"){
            $('#messages').prepend("<p>"+this.name+": "+this.text+"</p>" )        
          }
        })
      }
      event_check_timer = setTimeout(checkEvents, event_period)
    })
  }

  function nudge(){
    var miliseconds_idle = new Date().getTime() - last_interaction
    last_interaction = new Date().getTime()
    if(miliseconds_idle > 5000){
      clearTimeout(event_check_timer)
      checkEvents()
    }
  }

  $(document).mousemove(nudge)
  $(document).keypress(nudge)

  event_check_timer = setTimeout(checkEvents, event_period)  


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
