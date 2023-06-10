// Next largest element to right
// input : 4
// 1 3 2 4 
// output : 3 4 4 -1 


#include<bits/stdc++.h>

using namespace std ;

/*int main() 
{
    int n ;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }

    vector<int> vec;
    stack<int> s;

    for ( int i= n-1; i>=0;i--  ) {

        if( s.size() == 0) {
            vec.push_back(-1);
        }

        else if ( s.size() > 0 && s.top() > arr[i]) { // check this condition too
            vec.push_back(s.top() );
        }

        else if ( s.size() > 0 && s.top() <= arr[i] ) {
 
            while ( s.size() > 0 && s.top() <= arr[i] ) { // "IMP" loop 'until size becomes zero'
                s.pop();                   // or either 'top element becomes greater than arr[i]'
            }

            if ( s.size() == 0) {  
                vec.push_back(-1);  // conditon 
            }

            else if ( s.top() > arr[i] ) {
                vec.push_back(s.top()); // condition
            }

        }
        s.push(arr[i]);
    }
   reverse(vec.begin(), vec.end ());
   for( auto i = vec.begin(); i!= vec.end() ; i++) {
       cout<< *i << " "; 
   }

} */

vector<int> solve(int n,int arr[]) {
    vector<int>v;
    stack<int> s;
    int j=n-1;
    while(j >= 0){

        if(s.size() == 0){
            v.push_back(-1);
        }

        else if(s.size() > 0 && s.top() > arr[j]){
            v.push_back(s.top());
        }

        else if(s.size() > 0 && s.top() < arr[j]){
            while(s.size() > 0 && s.top() < arr[j]){
                s.pop();
            }
            if(s.size() == 0){
                v.push_back(-1);
            }
            else
                v.push_back(s.top());
        }
        s.push(arr[j]);
        j--;
    }
    reverse(v.begin() , v.end());
    return v;
}

int main() {
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    vector<int> v = solve(n,arr);
    for(int i=0;i<v.size();i++){
        cout<<v[i]<<" ";
    }
}