// 운동 결과 튜플 삭제
function resultDelete(id){
    answer = confirm("삭제할까요?");
    if(answer){
        location.href = "/result_delete?result_id=" + id;
    }
}