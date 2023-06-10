// time cpmolexity is O(n ^ 2)
#include<bits/stdc++.h>
using namespace std;

void BubbleSort(int arr[],int n){

    for(int k=0;k<n-1;k++){
        int flag = 0;
        for(int i=0;i<n-k-1;i++){
            if(arr[i] > arr[i+1]){
                swap(arr[i],arr[i+1]);
                flag =1;
            }
        }
        if(flag ==0) break;
    }
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    BubbleSort(arr,n);
    for(int i=0;i<n;i++){
        cout<<arr[i]<<" ";
    }
}