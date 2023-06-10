// nearest smaller element to left, smaller to left
// input : 5
//  4 5 2 10 8
// -1 4 -1 2 2


#include<bits/stdc++.h>

using namespace std ;
/*
int main() 
{
    int n ;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }

    vector<int> vec;
    stack<int> s;

    for(int i= 0; i < n; i++) {

        if( s.size() == 0) {
            vec.push_back(-1);
        }

        else if ( s.size() > 0 && s.top() < arr[i]) {
            vec.push_back(s.top());
        }

        else if ( s.size() > 0 && s.top() >= arr[i]) {
            while ( s.size() > 0 && s.top() >= arr[i]) {
                s.pop();
            }
            if ( s.size() == 0) {
                vec.push_back(-1);
            }
            else if (s.top() < arr[i]) {
                vec.push_back(s.top());
            }
        }
        s.push(arr[i]);
    }
    for(auto it = vec.begin(); it!=vec.end();it++) {
        cout<< *it<<" ";
    }

} */

vector<int> solve(int arr[],int n){
    vector<int> v;
    stack<int>s;
    int j=0;
    while(j<n){
        if(s.size() == 0){
            v.push_back(-1);
        }
        else if(s.size() > 0 && s.top() < arr[j]){
            v.push_back(s.top());
        }
        else if(s.size() > 0 && s.top() > arr[j]) {
            while(s.size() > 0 && s.top() > arr[j]){
                s.pop();
            }
            if(s.size() == 0){
                v.push_back(-1);
            }
            else if(s.size() > 0 && s.top() < arr[j]){
                v.push_back(s.top());
            }
        }
        s.push(arr[j]);
        j++;
    }
    return v;
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    vector<int> v =solve(arr,n);
    for(auto it=v.begin(); it != v.end();it++) {
        cout<< *it<<" ";
    }
}