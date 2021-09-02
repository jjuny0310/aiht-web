function resultDelete(id){
    answer = confirm(id+"삭제할까요?");
    if(answer){
        location.href = "/result_delete?id=" + id;
    }
}