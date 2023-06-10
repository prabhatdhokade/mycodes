


#include<bits/stdc++.h>

using namespace std;
/*selection sort
int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }

    for(int i=0;i<n-1;i++){
        for(int j=i+1;j<n;j++){
            if(arr[j] < arr[i]){
                int temp = arr[j];
                arr[j] = arr[i];
                arr[i] = temp;
            }
        }
    }
    for(int i=0;i<n;i++){
        cout<<arr[i]<<" ";
    }

} */

/* bubble sort
int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    int count = 1;
    while(count<n){
        for(int i=0;i<n-count;i++){
            if(arr[i] > arr[i+1]){
                int t = arr[i];
                arr[i] = arr[i+1];
                arr[i+1] = t;
            }
        }
        count++;
    }
    for(int i=0;i<n;i++){
        cout<<arr[i]<<" ";
    }
}
*/   
