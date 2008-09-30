function drop(piece,space){
  console.debug([piece,space])
}

window.addEvent('domready', function(event) {
  $$(".piece").each(function(piece){
    piece.addEvent('mousedown', function(){
      var clone = piece.clone().set('opacity',0.4).injectBefore(piece)
      drag = new Drag.Move(piece,{
        droppables:'.space',
        onDrop:drop
        })
    })
  })
})